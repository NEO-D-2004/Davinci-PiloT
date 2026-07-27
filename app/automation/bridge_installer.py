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

    # 1. Check for built-in 'resolve' object inside DaVinci Resolve workspace
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
        print("[DaVinci PiloT Bridge] Make sure DaVinci Resolve is running with an open project.")
    else:
        # 2. Extract Project Metadata
        pm = resolve_obj.GetProjectManager()
        proj = pm.GetCurrentProject() if pm else None

        if not proj:
            print("[DaVinci PiloT Bridge] WARNING: No project is currently open in DaVinci Resolve.")
        else:
            proj_name = proj.GetName()
            res_w = proj.GetSetting("timelineResolutionWidth") or "1920"
            res_h = proj.GetSetting("timelineResolutionHeight") or "1080"
            fps = proj.GetSetting("timelineFrameRate") or "24"
            tl_count = proj.GetTimelineCount() or 0

            # 3. Extract Active Timeline Metadata
            tl = proj.GetCurrentTimeline()
            tl_name = "None"
            v_tracks = 0
            a_tracks = 0
            total_clips = 0
            duration_tc = "00:00:00:00"
            start_tc = "01:00:00:00"

            if tl:
                tl_name = tl.GetName() or "Timeline 1"
                v_tracks = tl.GetTrackCount("video") or 0
                a_tracks = tl.GetTrackCount("audio") or 0
                
                # Count total items across video tracks
                for track_idx in range(1, v_tracks + 1):
                    items = tl.GetItemListInTrack("video", track_idx)
                    if items:
                        total_clips += len(items)

                # Also count audio items if video was 0
                if total_clips == 0:
                    for track_idx in range(1, a_tracks + 1):
                        items = tl.GetItemListInTrack("audio", track_idx)
                        if items:
                            total_clips += len(items)

                start_frame = tl.GetStartFrame() or 0
                start_tc = str(start_frame)

            # 4. Extract Media Pool Info
            mp = proj.GetMediaPool()
            root_folder = mp.GetRootFolder() if mp else None
            root_name = root_folder.GetName() if root_folder else "Master"
            clips_count = 0
            if root_folder:
                clips = root_folder.GetClipList()
                clips_count = len(clips) if clips else 0

            # 5. Build State Payload
            payload = {
                "resolve_version": str(getattr(resolve_obj, "GetVersion", lambda: ["21.0"])()[0] if hasattr(resolve_obj, "GetVersion") else "21.0"),
                "product_name": str(getattr(resolve_obj, "GetProductName", lambda: "DaVinci Resolve")() if hasattr(resolve_obj, "GetProductName") else "DaVinci Resolve"),
                "project": {
                    "name": proj_name,
                    "resolution": f"{res_w}x{res_h}",
                    "frame_rate": f"{fps} fps",
                    "timelines_count": tl_count,
                    "is_loaded": True
                },
                "timeline": {
                    "name": tl_name,
                    "start_timecode": start_tc,
                    "duration": duration_tc,
                    "video_tracks_count": v_tracks,
                    "audio_tracks_count": a_tracks,
                    "total_clips": total_clips,
                    "is_active": (tl is not None)
                },
                "media_pool": {
                    "root_folder_name": root_name,
                    "subfolders_count": 0,
                    "total_clips_count": clips_count
                }
            }

            # 6. POST Payload to DaVinci PiloT Desktop Application Server
            url = "http://127.0.0.1:18888/api/resolve_state"
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers={"Content-Type": "application/json"})

            try:
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        print(f"[DaVinci PiloT Bridge] SUCCESS! Connected & Synced '{proj_name}' -> DaVinci PiloT Desktop App!")
                    else:
                        print(f"[DaVinci PiloT Bridge] Server returned status: {resp.status}")
            except Exception as net_err:
                print(f"[DaVinci PiloT Bridge] Desktop App not responding on http://127.0.0.1:18888 ({net_err}). Make sure DaVinci PiloT is open!")

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
