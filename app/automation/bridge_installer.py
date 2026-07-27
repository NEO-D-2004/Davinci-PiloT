"""
DaVinci PiloT IPC Bridge Installer.
Deploys DaVinciPiloT_Bridge.py into DaVinci Resolve Fusion Scripts directory
to enable seamless integration for DaVinci Resolve Free and Studio users.
"""

import os
import sys
from pathlib import Path
from app.services.logger_service import app_logger

ROAMING_FUSION_SCRIPTS = Path(os.path.expandvars(r"%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"))

BRIDGE_SCRIPT_CONTENT = '''# DaVinci PiloT IPC Relay Bridge for DaVinci Resolve (Free & Studio)
# Automatically deployed by DaVinci PiloT Desktop Application

import sys
import os
import json
import urllib.request

print("==================================================")
print("  DaVinci PiloT Bridge - Syncing Resolve 21 State ")
print("==================================================")

try:
    resolve_obj = None

    # 1. Acquire Resolve handle
    if "resolve" in globals() and globals()["resolve"]:
        resolve_obj = globals()["resolve"]
    elif "bmd" in globals():
        resolve_obj = bmd.scriptapp("Resolve")
    else:
        try:
            import DaVinciResolveScript as bmd
            resolve_obj = bmd.scriptapp("Resolve")
        except Exception:
            pass

    if not resolve_obj:
        print("[DaVinci PiloT Bridge] ERROR: Could not acquire Resolve handle.")
    else:
        pm = resolve_obj.GetProjectManager()
        proj = pm.GetCurrentProject() if pm else None

        if not proj:
            print("[DaVinci PiloT Bridge] WARNING: No project is currently open.")
        else:
            proj_name = proj.GetName()
            res_w = proj.GetSetting("timelineResolutionWidth") or "1920"
            res_h = proj.GetSetting("timelineResolutionHeight") or "1080"
            fps_str = proj.GetSetting("timelineFrameRate") or "24"
            try:
                fps_val = float(fps_str)
            except Exception:
                fps_val = 24.0

            tl_count = proj.GetTimelineCount() or 0

            tl = proj.GetCurrentTimeline()
            tl_name = "None"
            v_tracks_count = 0
            a_tracks_count = 0
            total_clips_count = 0
            duration_tc = "00:00:00:00"
            start_tc = "01:00:00:00"

            video_tracks_data = []
            audio_tracks_data = []
            timeline_markers_data = []

            if tl:
                tl_name = tl.GetName() or "Timeline 1"
                v_tracks_count = tl.GetTrackCount("video") or 0
                a_tracks_count = tl.GetTrackCount("audio") or 0
                start_frame = tl.GetStartFrame() or 0
                start_tc = str(start_frame)

                # Extract Timeline Markers
                try:
                    markers_dict = tl.GetMarkers() or {}
                    for frame_idx, m_info in markers_dict.items():
                        timeline_markers_data.append({
                            "frame": int(frame_idx),
                            "timecode": str(frame_idx),
                            "color": m_info.get("color", "Blue"),
                            "name": m_info.get("name", ""),
                            "note": m_info.get("note", ""),
                            "duration": int(m_info.get("duration", 1))
                        })
                except Exception as m_err:
                    pass

                # Extract Video Tracks & Clips
                for t_idx in range(1, v_tracks_count + 1):
                    track_name = tl.GetTrackName("video", t_idx) or f"Video {t_idx}"
                    items = tl.GetItemListInTrack("video", t_idx) or []
                    clips_list = []

                    for clip_idx, item in enumerate(items, 1):
                        total_clips_count += 1
                        clip_name = item.GetName() or f"Clip {clip_idx}"
                        s_frame = item.GetStart() or 0
                        e_frame = item.GetEnd() or 0
                        dur_frame = item.GetDuration() or (e_frame - s_frame)
                        l_off = item.GetLeftOffset() or 0
                        r_off = item.GetRightOffset() or 0

                        # Media Pool Item Source Path
                        source_path = "N/A"
                        try:
                            mp_item = item.GetMediaPoolItem()
                            if mp_item:
                                props = mp_item.GetClipProperty() or {}
                                source_path = props.get("File Path") or props.get("Clip Name") or "N/A"
                        except Exception:
                            pass

                        # Flag & Color
                        flag_color = "None"
                        try:
                            flags = item.GetFlags()
                            if flags:
                                flag_color = str(flags[0]) if isinstance(flags, list) else str(flags)
                        except Exception:
                            pass

                        clip_color = "Default"
                        try:
                            clip_color = item.GetColor() or "Default"
                        except Exception:
                            pass

                        clips_list.append({
                            "clip_id": f"v_{t_idx}_{clip_idx}",
                            "name": clip_name,
                            "track_type": "video",
                            "track_index": t_idx,
                            "start_frame": s_frame,
                            "end_frame": e_frame,
                            "duration_frames": dur_frame,
                            "start_timecode": str(s_frame),
                            "end_timecode": str(e_frame),
                            "duration_timecode": str(dur_frame),
                            "left_offset": l_off,
                            "right_offset": r_off,
                            "source_path": source_path,
                            "flag_color": flag_color,
                            "clip_color": clip_color,
                            "markers": []
                        })

                    video_tracks_data.append({
                        "track_type": "video",
                        "track_index": t_idx,
                        "name": track_name,
                        "is_enabled": True,
                        "is_locked": False,
                        "clips": clips_list
                    })

                # Extract Audio Tracks & Clips
                for t_idx in range(1, a_tracks_count + 1):
                    track_name = tl.GetTrackName("audio", t_idx) or f"Audio {t_idx}"
                    items = tl.GetItemListInTrack("audio", t_idx) or []
                    clips_list = []

                    for clip_idx, item in enumerate(items, 1):
                        total_clips_count += 1
                        clip_name = item.GetName() or f"Audio Clip {clip_idx}"
                        s_frame = item.GetStart() or 0
                        e_frame = item.GetEnd() or 0
                        dur_frame = item.GetDuration() or (e_frame - s_frame)
                        l_off = item.GetLeftOffset() or 0
                        r_off = item.GetRightOffset() or 0

                        source_path = "N/A"
                        try:
                            mp_item = item.GetMediaPoolItem()
                            if mp_item:
                                props = mp_item.GetClipProperty() or {}
                                source_path = props.get("File Path") or props.get("Clip Name") or "N/A"
                        except Exception:
                            pass

                        clips_list.append({
                            "clip_id": f"a_{t_idx}_{clip_idx}",
                            "name": clip_name,
                            "track_type": "audio",
                            "track_index": t_idx,
                            "start_frame": s_frame,
                            "end_frame": e_frame,
                            "duration_frames": dur_frame,
                            "start_timecode": str(s_frame),
                            "end_timecode": str(e_frame),
                            "duration_timecode": str(dur_frame),
                            "left_offset": l_off,
                            "right_offset": r_off,
                            "source_path": source_path,
                            "flag_color": "None",
                            "clip_color": "Default",
                            "markers": []
                        })

                    audio_tracks_data.append({
                        "track_type": "audio",
                        "track_index": t_idx,
                        "name": track_name,
                        "is_enabled": True,
                        "is_locked": False,
                        "clips": clips_list
                    })

            # Extract Media Pool Info
            mp = proj.GetMediaPool()
            root_folder = mp.GetRootFolder() if mp else None
            root_name = root_folder.GetName() if root_folder else "Master"
            clips_count = 0
            if root_folder:
                clips = root_folder.GetClipList()
                clips_count = len(clips) if clips else 0

            # Build Full Payload
            payload = {
                "resolve_version": str(getattr(resolve_obj, "GetVersion", lambda: ["21.0"])()[0] if hasattr(resolve_obj, "GetVersion") else "21.0"),
                "product_name": str(getattr(resolve_obj, "GetProductName", lambda: "DaVinci Resolve")() if hasattr(resolve_obj, "GetProductName") else "DaVinci Resolve"),
                "project": {
                    "name": proj_name,
                    "resolution": f"{res_w}x{res_h}",
                    "frame_rate": f"{fps_str} fps",
                    "timelines_count": tl_count,
                    "is_loaded": True
                },
                "timeline": {
                    "name": tl_name,
                    "start_timecode": start_tc,
                    "duration": duration_tc,
                    "video_tracks_count": v_tracks_count,
                    "audio_tracks_count": a_tracks_count,
                    "total_clips": total_clips_count,
                    "is_active": (tl is not None)
                },
                "media_pool": {
                    "root_folder_name": root_name,
                    "subfolders_count": 0,
                    "total_clips_count": clips_count
                },
                "timeline_structure": {
                    "name": tl_name,
                    "start_timecode": start_tc,
                    "duration_frames": 0,
                    "duration_timecode": duration_tc,
                    "fps": fps_val,
                    "video_tracks": video_tracks_data,
                    "audio_tracks": audio_tracks_data,
                    "markers": timeline_markers_data
                }
            }

            url = "http://127.0.0.1:18888/api/resolve_state"
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})

            try:
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        print(f"[DaVinci PiloT Bridge] SUCCESS! Synced Timeline Structure ({total_clips_count} clips across {v_tracks_count}V / {a_tracks_count}A tracks) -> DaVinci PiloT!")
                    else:
                        print(f"[DaVinci PiloT Bridge] Server status: {resp.status}")
            except Exception as net_err:
                print(f"[DaVinci PiloT Bridge] Server error: {net_err}")

except Exception as main_err:
    print(f"[DaVinci PiloT Bridge] Unexpected error: {main_err}")

print("==================================================")
'''


def install_resolve_bridge() -> bool:
    """Deploy DaVinciPiloT_Bridge.py into Resolve Utility scripts directory."""
    try:
        if not ROAMING_FUSION_SCRIPTS.exists():
            ROAMING_FUSION_SCRIPTS.mkdir(parents=True, exist_ok=True)

        bridge_file = ROAMING_FUSION_SCRIPTS / "DaVinciPiloT_Bridge.py"
        with open(bridge_file, "w", encoding="utf-8") as f:
            f.write(BRIDGE_SCRIPT_CONTENT)

        app_logger.info(f"Deployed DaVinci PiloT Bridge script to: {bridge_file}")
        return True
    except Exception as e:
        app_logger.warning(f"Could not deploy DaVinci PiloT Bridge script: {e}")
        return False
