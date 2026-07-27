"""
Frame Sampler & Audio Extraction Module for DaVinci PiloT.
Extracts sampled video keyframes and audio tracks using FFmpeg instead of sending raw long video files to vision LLMs.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from app.settings import settings_manager
from app.services.logger_service import app_logger


class FrameSampler:
    """Handles video frame extraction and scene boundary sampling."""

    def __init__(self, sample_rate_fps: float = 1.0, detect_scene_changes: bool = True) -> None:
        fs_settings = settings_manager.get("frame_sampling", {})
        self.sample_rate_fps = fs_settings.get("sample_rate_fps", sample_rate_fps)
        self.detect_scene_changes = fs_settings.get("detect_scene_changes", detect_scene_changes)
        self.ffmpeg_path = fs_settings.get("ffmpeg_path", "ffmpeg")

    def get_sample_config(self) -> Dict[str, Any]:
        """Return frame sampling configuration."""
        return {
            "sample_rate_fps": self.sample_rate_fps,
            "detect_scene_changes": self.detect_scene_changes,
            "ffmpeg_path": self.ffmpeg_path
        }

    def prepare_sampling_manifest(self, video_path: str) -> Dict[str, Any]:
        """Generate frame extraction manifest for a given video file."""
        v_path = Path(video_path)
        return {
            "video_path": str(v_path),
            "video_name": v_path.name,
            "sample_rate_fps": self.sample_rate_fps,
            "scene_detection_enabled": self.detect_scene_changes,
            "output_frame_format": "jpg",
            "output_audio_format": "wav"
        }
