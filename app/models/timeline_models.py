"""
Timeline data models for DaVinci PiloT.
Structures Tracks, Clip Items, Markers, and Timeline layouts parsed from DaVinci Resolve.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class TimelineMarker:
    """Represents a timeline or clip marker in DaVinci Resolve."""
    frame: int = 0
    timecode: str = "00:00:00:00"
    color: str = "Blue"
    name: str = ""
    note: str = ""
    duration: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame": self.frame,
            "timecode": self.timecode,
            "color": self.color,
            "name": self.name,
            "note": self.note,
            "duration": self.duration,
        }


@dataclass
class ClipItem:
    """Represents an individual clip/item on a DaVinci Resolve timeline track."""
    clip_id: str = ""
    name: str = "Untitled Clip"
    track_type: str = "video"  # "video" or "audio"
    track_index: int = 1
    start_frame: int = 0
    end_frame: int = 0
    duration_frames: int = 0
    start_timecode: str = "00:00:00:00"
    end_timecode: str = "00:00:00:00"
    duration_timecode: str = "00:00:00:00"
    left_offset: int = 0
    right_offset: int = 0
    source_path: str = "N/A"
    flag_color: str = "None"
    clip_color: str = "Default"
    markers: List[TimelineMarker] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "name": self.name,
            "track_type": self.track_type,
            "track_index": self.track_index,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "duration_frames": self.duration_frames,
            "start_timecode": self.start_timecode,
            "end_timecode": self.end_timecode,
            "duration_timecode": self.duration_timecode,
            "left_offset": self.left_offset,
            "right_offset": self.right_offset,
            "source_path": self.source_path,
            "flag_color": self.flag_color,
            "clip_color": self.clip_color,
            "markers": [m.to_dict() for m in self.markers],
        }


@dataclass
class TrackInfo:
    """Represents a timeline video or audio track."""
    track_type: str = "video"  # "video" or "audio"
    track_index: int = 1
    name: str = "Track 1"
    is_enabled: bool = True
    is_locked: bool = False
    clips: List[ClipItem] = field(default_factory=list)

    @property
    def total_clips(self) -> int:
        return len(self.clips)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_type": self.track_type,
            "track_index": self.track_index,
            "name": self.name,
            "is_enabled": self.is_enabled,
            "is_locked": self.is_locked,
            "total_clips": self.total_clips,
            "clips": [c.to_dict() for c in self.clips],
        }


@dataclass
class TimelineStructure:
    """Aggregated model representing complete DaVinci Resolve Timeline structure."""
    name: str = "None"
    start_timecode: str = "01:00:00:00"
    duration_frames: int = 0
    duration_timecode: str = "00:00:00:00"
    fps: float = 24.0
    video_tracks: List[TrackInfo] = field(default_factory=list)
    audio_tracks: List[TrackInfo] = field(default_factory=list)
    markers: List[TimelineMarker] = field(default_factory=list)

    @property
    def total_video_clips(self) -> int:
        return sum(t.total_clips for t in self.video_tracks)

    @property
    def total_audio_clips(self) -> int:
        return sum(t.total_clips for t in self.audio_tracks)

    @property
    def total_clips(self) -> int:
        return self.total_video_clips + self.total_audio_clips

    def get_all_clips(self) -> List[ClipItem]:
        clips: List[ClipItem] = []
        for track in self.video_tracks + self.audio_tracks:
            clips.extend(track.clips)
        return clips

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "start_timecode": self.start_timecode,
            "duration_frames": self.duration_frames,
            "duration_timecode": self.duration_timecode,
            "fps": self.fps,
            "total_clips": self.total_clips,
            "total_video_clips": self.total_video_clips,
            "total_audio_clips": self.total_audio_clips,
            "video_tracks": [vt.to_dict() for vt in self.video_tracks],
            "audio_tracks": [at.to_dict() for at in self.audio_tracks],
            "markers": [m.to_dict() for m in self.markers],
        }
