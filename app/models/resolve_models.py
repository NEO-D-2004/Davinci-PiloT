"""
Data models for DaVinci Resolve connection, active project, timeline, and media pool states.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class ProjectInfo:
    """Represents active DaVinci Resolve project metadata."""
    name: str = "None"
    resolution: str = "N/A"
    frame_rate: str = "N/A"
    timelines_count: int = 0
    video_format: str = "N/A"
    is_loaded: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "resolution": self.resolution,
            "frame_rate": self.frame_rate,
            "timelines_count": self.timelines_count,
            "video_format": self.video_format,
            "is_loaded": self.is_loaded,
        }


@dataclass
class TimelineInfo:
    """Represents active DaVinci Resolve timeline metadata."""
    name: str = "None"
    start_timecode: str = "00:00:00:00"
    duration_frames: int = 0
    duration_timecode: str = "00:00:00:00"
    video_tracks_count: int = 0
    audio_tracks_count: int = 0
    total_clips: int = 0
    is_active: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "start_timecode": self.start_timecode,
            "duration_frames": self.duration_frames,
            "duration_timecode": self.duration_timecode,
            "video_tracks_count": self.video_tracks_count,
            "audio_tracks_count": self.audio_tracks_count,
            "total_clips": self.total_clips,
            "is_active": self.is_active,
        }


@dataclass
class MediaPoolInfo:
    """Represents DaVinci Resolve Media Pool metadata."""
    root_folder_name: str = "Master"
    subfolders_count: int = 0
    total_clips_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_folder_name": self.root_folder_name,
            "subfolders_count": self.subfolders_count,
            "total_clips_count": self.total_clips_count,
        }


from app.models.timeline_models import TimelineStructure


@dataclass
class ResolveState:
    """Aggregated DaVinci Resolve state model."""
    is_connected: bool = False
    resolve_version: str = "Unknown"
    product_name: str = "DaVinci Resolve"
    error_message: Optional[str] = None
    project: ProjectInfo = field(default_factory=ProjectInfo)
    timeline: TimelineInfo = field(default_factory=TimelineInfo)
    media_pool: MediaPoolInfo = field(default_factory=MediaPoolInfo)
    timeline_structure: Optional[TimelineStructure] = None

