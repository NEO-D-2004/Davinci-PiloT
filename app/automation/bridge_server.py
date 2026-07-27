"""
DaVinci PiloT Local Bridge Server Module.
Runs a lightweight HTTP server on http://127.0.0.1:18888 to receive real-time state 
and command execution callbacks from DaVinciPiloT_Bridge script running inside DaVinci Resolve.
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any, Callable, List
from app.models.resolve_models import ResolveState, ProjectInfo, TimelineInfo, MediaPoolInfo
from app.models.timeline_models import TimelineStructure, TrackInfo, ClipItem, TimelineMarker
from app.models.mediapool_models import MediaPoolStructure, MediaBin, MediaAsset
from app.services.logger_service import app_logger

BRIDGE_PORT = 18888
_server_instance: Optional[HTTPServer] = None
_server_thread: Optional[threading.Thread] = None
_state_callback: Optional[Callable[[ResolveState], None]] = None


def parse_timeline_structure(ts_data: Dict[str, Any]) -> TimelineStructure:
    """Helper to convert JSON dictionary into TimelineStructure object graph."""
    if not ts_data:
        return TimelineStructure()

    video_tracks: List[TrackInfo] = []
    for vt in ts_data.get("video_tracks", []):
        clips: List[ClipItem] = []
        for c in vt.get("clips", []):
            markers = [
                TimelineMarker(
                    frame=m.get("frame", 0),
                    timecode=m.get("timecode", "0"),
                    color=m.get("color", "Blue"),
                    name=m.get("name", ""),
                    note=m.get("note", ""),
                    duration=m.get("duration", 1)
                ) for m in c.get("markers", [])
            ]
            clips.append(
                ClipItem(
                    clip_id=c.get("clip_id", ""),
                    name=c.get("name", "Untitled Clip"),
                    track_type="video",
                    track_index=c.get("track_index", 1),
                    start_frame=c.get("start_frame", 0),
                    end_frame=c.get("end_frame", 0),
                    duration_frames=c.get("duration_frames", 0),
                    start_timecode=c.get("start_timecode", "00:00:00:00"),
                    end_timecode=c.get("end_timecode", "00:00:00:00"),
                    duration_timecode=c.get("duration_timecode", "00:00:00:00"),
                    left_offset=c.get("left_offset", 0),
                    right_offset=c.get("right_offset", 0),
                    source_path=c.get("source_path", "N/A"),
                    flag_color=c.get("flag_color", "None"),
                    clip_color=c.get("clip_color", "Default"),
                    markers=markers
                )
            )
        video_tracks.append(
            TrackInfo(
                track_type="video",
                track_index=vt.get("track_index", 1),
                name=vt.get("name", "Video Track"),
                is_enabled=vt.get("is_enabled", True),
                is_locked=vt.get("is_locked", False),
                clips=clips
            )
        )

    audio_tracks: List[TrackInfo] = []
    for at in ts_data.get("audio_tracks", []):
        clips: List[ClipItem] = []
        for c in at.get("clips", []):
            clips.append(
                ClipItem(
                    clip_id=c.get("clip_id", ""),
                    name=c.get("name", "Untitled Audio Clip"),
                    track_type="audio",
                    track_index=c.get("track_index", 1),
                    start_frame=c.get("start_frame", 0),
                    end_frame=c.get("end_frame", 0),
                    duration_frames=c.get("duration_frames", 0),
                    start_timecode=c.get("start_timecode", "00:00:00:00"),
                    end_timecode=c.get("end_timecode", "00:00:00:00"),
                    duration_timecode=c.get("duration_timecode", "00:00:00:00"),
                    left_offset=c.get("left_offset", 0),
                    right_offset=c.get("right_offset", 0),
                    source_path=c.get("source_path", "N/A"),
                    flag_color=c.get("flag_color", "None"),
                    clip_color=c.get("clip_color", "Default"),
                    markers=[]
                )
            )
        audio_tracks.append(
            TrackInfo(
                track_type="audio",
                track_index=at.get("track_index", 1),
                name=at.get("name", "Audio Track"),
                is_enabled=at.get("is_enabled", True),
                is_locked=at.get("is_locked", False),
                clips=clips
            )
        )

    markers: List[TimelineMarker] = [
        TimelineMarker(
            frame=m.get("frame", 0),
            timecode=m.get("timecode", "0"),
            color=m.get("color", "Blue"),
            name=m.get("name", ""),
            note=m.get("note", ""),
            duration=m.get("duration", 1)
        ) for m in ts_data.get("markers", [])
    ]

    return TimelineStructure(
        name=ts_data.get("name", "Timeline"),
        start_timecode=ts_data.get("start_timecode", "01:00:00:00"),
        duration_frames=ts_data.get("duration_frames", 0),
        duration_timecode=ts_data.get("duration_timecode", "00:00:00:00"),
        fps=float(ts_data.get("fps", 24.0)),
        video_tracks=video_tracks,
        audio_tracks=audio_tracks,
        markers=markers
    )


def parse_bin_recursive(b_data: Dict[str, Any]) -> MediaBin:
    """Helper to convert JSON bin structure recursively."""
    if not b_data:
        return MediaBin()

    assets: List[MediaAsset] = []
    for a in b_data.get("assets", []):
        assets.append(
            MediaAsset(
                media_id=a.get("media_id", ""),
                name=a.get("name", "Untitled Asset"),
                asset_type=a.get("asset_type", "Video"),
                file_path=a.get("file_path", "N/A"),
                resolution=a.get("resolution", "1920x1080"),
                fps=str(a.get("fps", "24.0")),
                duration=a.get("duration", "00:00:00:00"),
                duration_frames=a.get("duration_frames", 0),
                video_codec=a.get("video_codec", "H.264"),
                audio_codec=a.get("audio_codec", "AAC"),
                audio_channels=int(a.get("audio_channels", 2)),
                file_size=a.get("file_size", "N/A"),
                date_modified=a.get("date_modified", "N/A"),
                clip_color=a.get("clip_color", "Default"),
                flag_color=a.get("flag_color", "None"),
                scene=a.get("scene", ""),
                shot=a.get("shot", ""),
                take=a.get("take", ""),
                good_take=bool(a.get("good_take", False)),
                comments=a.get("comments", ""),
                bin_name=a.get("bin_name", "Master")
            )
        )

    subfolders: List[MediaBin] = []
    for sub in b_data.get("subfolders", []):
        subfolders.append(parse_bin_recursive(sub))

    return MediaBin(
        bin_id=b_data.get("bin_id", "bin_master"),
        name=b_data.get("name", "Master"),
        folder_path=b_data.get("folder_path", "Master"),
        subfolders=subfolders,
        assets=assets
    )


def parse_mediapool_structure(mp_data: Dict[str, Any]) -> MediaPoolStructure:
    """Helper to convert JSON media_pool_structure into MediaPoolStructure object graph."""
    if not mp_data:
        return MediaPoolStructure()

    root_b_data = mp_data.get("root_bin", {})
    root_bin = parse_bin_recursive(root_b_data)

    return MediaPoolStructure(root_bin=root_bin)


class BridgeRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP POST state sync requests from DaVinciPiloT_Bridge inside Resolve."""

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress default HTTP request logging
        pass

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "app": "DaVinci PiloT"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self) -> None:
        if self.path == "/api/resolve_state":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                data = json.loads(body)

                # Parse ProjectInfo
                p_data = data.get("project", {})
                project = ProjectInfo(
                    name=p_data.get("name", "Unknown"),
                    resolution=p_data.get("resolution", "1920x1080"),
                    frame_rate=p_data.get("frame_rate", "24.0 fps"),
                    timelines_count=p_data.get("timelines_count", 0),
                    is_loaded=p_data.get("is_loaded", True)
                )

                # Parse TimelineInfo
                t_data = data.get("timeline", {})
                timeline = TimelineInfo(
                    name=t_data.get("name", "None"),
                    start_timecode=t_data.get("start_timecode", "01:00:00:00"),
                    duration_timecode=t_data.get("duration", "00:00:00:00"),
                    video_tracks_count=t_data.get("video_tracks_count", 0),
                    audio_tracks_count=t_data.get("audio_tracks_count", 0),
                    total_clips=t_data.get("total_clips", 0),
                    is_active=t_data.get("is_active", True)
                )

                # Parse MediaPoolInfo
                m_data = data.get("media_pool", {})
                media_pool = MediaPoolInfo(
                    root_folder_name=m_data.get("root_folder_name", "Master"),
                    subfolders_count=m_data.get("subfolders_count", 0),
                    total_clips_count=m_data.get("total_clips_count", 0)
                )

                # Parse TimelineStructure
                ts_data = data.get("timeline_structure", {})
                timeline_struct = parse_timeline_structure(ts_data)

                # Parse MediaPoolStructure
                mp_struct_data = data.get("media_pool_structure", {})
                mediapool_struct = parse_mediapool_structure(mp_struct_data)

                state = ResolveState(
                    is_connected=True,
                    resolve_version=data.get("resolve_version", "21.0"),
                    product_name=data.get("product_name", "DaVinci Resolve"),
                    project=project,
                    timeline=timeline,
                    media_pool=media_pool,
                    timeline_structure=timeline_struct,
                    media_pool_structure=mediapool_struct,
                    error_message=None
                )

                app_logger.info(
                    f"Received live state from DaVinci PiloT Bridge: Project='{project.name}', "
                    f"Timeline='{timeline.name}' ({timeline_struct.total_clips} clips), "
                    f"MediaPool ({mediapool_struct.total_assets} assets in Bins)"
                )

                # Invoke UI update callback
                if _state_callback:
                    _state_callback(state)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response_payload = json.dumps({"status": "success", "message": "State updated"}).encode("utf-8")
                self.wfile.write(response_payload)
            except Exception as e:
                app_logger.error(f"Error handling bridge POST request: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def start_bridge_server(on_state_received: Callable[[ResolveState], None]) -> bool:
    """Start local HTTP server in background thread."""
    global _server_instance, _server_thread, _state_callback

    _state_callback = on_state_received

    if _server_instance is not None:
        return True

    try:
        _server_instance = HTTPServer(("127.0.0.1", BRIDGE_PORT), BridgeRequestHandler)
        _server_thread = threading.Thread(target=_server_instance.serve_forever, daemon=True)
        _server_thread.start()
        app_logger.info(f"Started DaVinci PiloT Local Bridge Server on http://127.0.0.1:{BRIDGE_PORT}")
        return True
    except Exception as e:
        app_logger.error(f"Failed to start Local Bridge Server on port {BRIDGE_PORT}: {e}")
        return False


def stop_bridge_server() -> None:
    """Stop local HTTP server."""
    global _server_instance, _server_thread
    if _server_instance:
        _server_instance.shutdown()
        _server_instance = None
        _server_thread = None
        app_logger.info("Stopped DaVinci PiloT Local Bridge Server.")
