"""
Data models for Milestone 5 NVIDIA NIM Multi-Agent Vision & Audio Analyzer.
Structures Transcripts, Silence Gaps, Visual Frame Insights, and Smart Cut Proposals.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class TranscriptSegment:
    """Represents a timestamped speech segment from Nemotron ASR."""
    segment_id: str = ""
    start_sec: float = 0.0
    end_sec: float = 0.0
    start_timecode: str = "00:00:00:00"
    end_timecode: str = "00:00:00:00"
    text: str = ""
    speaker: str = "Speaker 1"
    confidence: float = 0.99
    is_silence: bool = False
    is_filler: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "start_sec": self.start_sec,
            "end_sec": self.end_sec,
            "start_timecode": self.start_timecode,
            "end_timecode": self.end_timecode,
            "text": self.text,
            "speaker": self.speaker,
            "confidence": self.confidence,
            "is_silence": self.is_silence,
            "is_filler": self.is_filler,
        }


@dataclass
class SilenceGap:
    """Represents a detected silence gap candidate for automatic ripple removal."""
    gap_id: str = ""
    start_sec: float = 0.0
    end_sec: float = 0.0
    start_timecode: str = "00:00:00:00"
    end_timecode: str = "00:00:00:00"
    duration_sec: float = 0.0
    recommended_action: str = "Ripple Cut Silence"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "start_sec": self.start_sec,
            "end_sec": self.end_sec,
            "start_timecode": self.start_timecode,
            "end_timecode": self.end_timecode,
            "duration_sec": self.duration_sec,
            "recommended_action": self.recommended_action,
        }


@dataclass
class VisualFrameInsight:
    """Represents multimodal vision insight for a sampled keyframe from MiniMax M3."""
    frame_idx: int = 0
    timestamp_sec: float = 0.0
    timecode: str = "00:00:00:00"
    frame_path: str = ""
    scene_description: str = ""
    detected_objects: List[str] = field(default_factory=list)
    camera_movement: str = "Static"
    quality_score: float = 8.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_idx": self.frame_idx,
            "timestamp_sec": self.timestamp_sec,
            "timecode": self.timecode,
            "frame_path": self.frame_path,
            "scene_description": self.scene_description,
            "detected_objects": self.detected_objects,
            "camera_movement": self.camera_movement,
            "quality_score": self.quality_score,
        }


@dataclass
class SmartCutProposal:
    """Represents an AI-generated recommended cut/edit proposal from GLM-5.2 Master Agent."""
    cut_id: str = ""
    clip_name: str = "Clip 1"
    start_sec: float = 0.0
    end_sec: float = 0.0
    start_timecode: str = "00:00:00:00"
    end_timecode: str = "00:00:00:00"
    cut_type: str = "Silence"  # "Silence", "Filler Word", "Bad Take", "Scene Transition"
    reason: str = "Remove long pause (> 1.5s)"
    priority: str = "HIGH"  # "HIGH", "MEDIUM", "LOW"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cut_id": self.cut_id,
            "clip_name": self.clip_name,
            "start_sec": self.start_sec,
            "end_sec": self.end_sec,
            "start_timecode": self.start_timecode,
            "end_timecode": self.end_timecode,
            "cut_type": self.cut_type,
            "reason": self.reason,
            "priority": self.priority,
        }


@dataclass
class AnalysisReport:
    """Aggregated Multi-Agent AI Analysis Report."""
    asset_name: str = "Untitled Media"
    total_duration_sec: float = 0.0
    segments: List[TranscriptSegment] = field(default_factory=list)
    silence_gaps: List[SilenceGap] = field(default_factory=list)
    frame_insights: List[VisualFrameInsight] = field(default_factory=list)
    cut_proposals: List[SmartCutProposal] = field(default_factory=list)

    @property
    def total_silence_time(self) -> float:
        return sum(g.duration_sec for g in self.silence_gaps)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_name": self.asset_name,
            "total_duration_sec": self.total_duration_sec,
            "total_silence_time": self.total_silence_time,
            "segments": [s.to_dict() for s in self.segments],
            "silence_gaps": [g.to_dict() for g in self.silence_gaps],
            "frame_insights": [fi.to_dict() for fi in self.frame_insights],
            "cut_proposals": [cp.to_dict() for cp in self.cut_proposals],
        }
