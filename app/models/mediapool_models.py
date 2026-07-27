"""
Media Pool data models for DaVinci PiloT.
Structures Bins, Media Assets, Codec metadata, and Folder hierarchies parsed from DaVinci Resolve.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class MediaAsset:
    """Represents an individual media asset clip in the DaVinci Resolve Media Pool."""
    media_id: str = ""
    name: str = "Untitled Asset"
    asset_type: str = "Video"  # "Video", "Audio", "Image", "Timeline", "Multicam"
    file_path: str = "N/A"
    resolution: str = "1920x1080"
    fps: str = "24.0"
    duration: str = "00:00:00:00"
    duration_frames: int = 0
    video_codec: str = "H.264"
    audio_codec: str = "AAC"
    audio_channels: int = 2
    file_size: str = "N/A"
    date_modified: str = "N/A"
    clip_color: str = "Default"
    flag_color: str = "None"
    scene: str = ""
    shot: str = ""
    take: str = ""
    good_take: bool = False
    comments: str = ""
    bin_name: str = "Master"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "media_id": self.media_id,
            "name": self.name,
            "asset_type": self.asset_type,
            "file_path": self.file_path,
            "resolution": self.resolution,
            "fps": self.fps,
            "duration": self.duration,
            "duration_frames": self.duration_frames,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "audio_channels": self.audio_channels,
            "file_size": self.file_size,
            "date_modified": self.date_modified,
            "clip_color": self.clip_color,
            "flag_color": self.flag_color,
            "scene": self.scene,
            "shot": self.shot,
            "take": self.take,
            "good_take": self.good_take,
            "comments": self.comments,
            "bin_name": self.bin_name,
        }


@dataclass
class MediaBin:
    """Represents a Media Pool Bin folder."""
    bin_id: str = ""
    name: str = "Master"
    folder_path: str = "Master"
    subfolders: List['MediaBin'] = field(default_factory=list)
    assets: List[MediaAsset] = field(default_factory=list)

    @property
    def total_assets(self) -> int:
        count = len(self.assets)
        for sub in self.subfolders:
            count += sub.total_assets
        return count

    def get_all_assets(self) -> List[MediaAsset]:
        result: List[MediaAsset] = list(self.assets)
        for sub in self.subfolders:
            result.extend(sub.get_all_assets())
        return result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bin_id": self.bin_id,
            "name": self.name,
            "folder_path": self.folder_path,
            "total_assets": self.total_assets,
            "subfolders": [sub.to_dict() for sub in self.subfolders],
            "assets": [a.to_dict() for a in self.assets],
        }


@dataclass
class MediaPoolStructure:
    """Aggregated model representing complete DaVinci Resolve Media Pool structure."""
    root_bin: MediaBin = field(default_factory=MediaBin)

    @property
    def total_assets(self) -> int:
        return self.root_bin.total_assets

    @property
    def total_video_assets(self) -> int:
        return len([a for a in self.get_all_assets() if a.asset_type.lower() == "video"])

    @property
    def total_audio_assets(self) -> int:
        return len([a for a in self.get_all_assets() if a.asset_type.lower() == "audio"])

    @property
    def total_image_assets(self) -> int:
        return len([a for a in self.get_all_assets() if a.asset_type.lower() in ("image", "still")])

    @property
    def total_good_takes(self) -> int:
        return len([a for a in self.get_all_assets() if a.good_take])

    def get_all_assets(self) -> List[MediaAsset]:
        return self.root_bin.get_all_assets()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_assets": self.total_assets,
            "total_video_assets": self.total_video_assets,
            "total_audio_assets": self.total_audio_assets,
            "total_image_assets": self.total_image_assets,
            "total_good_takes": self.total_good_takes,
            "root_bin": self.root_bin.to_dict(),
        }
