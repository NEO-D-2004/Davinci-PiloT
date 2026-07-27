"""
DaVinci PiloT Local Bridge Server Module.
Runs a lightweight HTTP server on http://127.0.0.1:18888 to receive real-time state 
and command execution callbacks from DaVinciPiloT_Bridge script running inside DaVinci Resolve.
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any, Callable
from app.models.resolve_models import ResolveState, ProjectInfo, TimelineInfo, MediaPoolInfo
from app.services.logger_service import app_logger

BRIDGE_PORT = 18888
_server_instance: Optional[HTTPServer] = None
_server_thread: Optional[threading.Thread] = None
_state_callback: Optional[Callable[[ResolveState], None]] = None


class BridgeRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP POST state sync requests from DaVinciPiloT_Bridge inside Resolve."""

    def log_message(self, format: str, *args: Any) -> None:
        # Suppress default HTTP request logging to clean stdout
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

                state = ResolveState(
                    is_connected=True,
                    resolve_version=data.get("resolve_version", "21.0"),
                    product_name=data.get("product_name", "DaVinci Resolve"),
                    project=project,
                    timeline=timeline,
                    media_pool=media_pool,
                    error_message=None
                )

                app_logger.info(f"Received live state from DaVinci PiloT Bridge: Project='{project.name}', Timeline='{timeline.name}' ({timeline.total_clips} clips)")

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
