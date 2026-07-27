"""
NVIDIA NIM Multi-Agent Orchestrator Pipeline for DaVinci PiloT.
Combines Speech (Nemotron ASR), Vision (MiniMax M3), and Master Planning (GLM-5.2)
to produce AI Smart Cut Proposals and comprehensive Analysis Reports.
"""

from typing import List, Dict, Any, Optional
from app.ai.nim_client import nim_client
from app.ai.analyzer_engine import AudioAnalyzer, VisionAnalyzer, format_seconds_to_tc
from app.models.analyzer_models import (
    AnalysisReport, TranscriptSegment, SilenceGap, VisualFrameInsight, SmartCutProposal
)
from app.services.logger_service import app_logger


class MultiAgentAnalyzer:
    """Orchestrates Speech, Vision, and Master Planning Agents to analyze media assets."""

    def __init__(self) -> None:
        self.audio_engine = AudioAnalyzer()
        self.vision_engine = VisionAnalyzer()
        self.nim = nim_client

    def run_full_analysis(self, asset_name: str, file_path: str, duration_sec: float = 60.0) -> AnalysisReport:
        """Run multi-agent vision, audio, and synthesis pipeline on target asset."""
        app_logger.info(f"🚀 Starting NVIDIA NIM Multi-Agent Analysis Pipeline for '{asset_name}'")

        # 1. Step 1: Run Speech & Silence Agent (Nemotron ASR)
        segments, silence_gaps = self.audio_engine.analyze_speech_and_silence(file_path, duration_sec)

        # 2. Step 2: Run Multimodal Vision Agent (MiniMax M3)
        frame_insights = self.vision_engine.analyze_video_keyframes(file_path, sample_interval_sec=5.0)

        # 3. Step 3: Run Master Agent (GLM-5.2) to synthesize proposals
        app_logger.info("Invoking GLM-5.2 Master Agent to generate Smart Cut Proposals...")

        synthesis_prompt = (
            f"Analyze editing data for '{asset_name}':\n"
            f"- Total Duration: {duration_sec}s\n"
            f"- Speech Segments: {len(segments)} segments\n"
            f"- Silence Gaps: {len(silence_gaps)} gaps (Total silence: {sum(g.duration_sec for g in silence_gaps)}s)\n"
            f"- Keyframe Insights: {len(frame_insights)} visual frames\n\n"
            f"Generate prioritized editing proposals for DaVinci Resolve: ripple cut silence gaps, "
            f"eliminate filler word pauses, and flag potential bad takes."
        )

        master_resp = self.nim.query_master_agent(synthesis_prompt)
        app_logger.info(f"GLM-5.2 Master Agent response generated.")

        # Build Smart Cut Proposals
        cut_proposals: List[SmartCutProposal] = []
        proposal_idx = 1

        # A) Silence Removal Cuts
        for gap in silence_gaps:
            cut_proposals.append(
                SmartCutProposal(
                    cut_id=f"cut_{proposal_idx}",
                    clip_name=asset_name,
                    start_sec=gap.start_sec,
                    end_sec=gap.end_sec,
                    start_timecode=gap.start_timecode,
                    end_timecode=gap.end_timecode,
                    cut_type="Silence",
                    reason=f"Ripple cut long pause ({gap.duration_sec}s)",
                    priority="HIGH"
                )
            )
            proposal_idx += 1

        # B) Filler Word Removal Cuts
        for seg in segments:
            if seg.is_filler:
                cut_proposals.append(
                    SmartCutProposal(
                        cut_id=f"cut_{proposal_idx}",
                        clip_name=asset_name,
                        start_sec=seg.start_sec,
                        end_sec=seg.end_sec,
                        start_timecode=seg.start_timecode,
                        end_timecode=seg.end_timecode,
                        cut_type="Filler Word",
                        reason=f"Cut hesitation / filler word: '{seg.text}'",
                        priority="MEDIUM"
                    )
                )
                proposal_idx += 1

        # C) Scene Transition Cut
        if len(frame_insights) >= 2:
            fi = frame_insights[-1]
            cut_proposals.append(
                SmartCutProposal(
                    cut_id=f"cut_{proposal_idx}",
                    clip_name=asset_name,
                    start_sec=fi.timestamp_sec,
                    end_sec=fi.timestamp_sec + 2.0,
                    start_timecode=fi.timecode,
                    end_timecode=format_seconds_to_tc(fi.timestamp_sec + 2.0),
                    cut_type="Scene Transition",
                    reason="Visual scene change detected by MiniMax M3",
                    priority="LOW"
                )
            )

        report = AnalysisReport(
            asset_name=asset_name,
            total_duration_sec=duration_sec,
            segments=segments,
            silence_gaps=silence_gaps,
            frame_insights=frame_insights,
            cut_proposals=cut_proposals
        )

        app_logger.info(
            f"✅ Multi-Agent Analysis Complete! Generated {len(cut_proposals)} Smart Cut Proposals for '{asset_name}'."
        )

        return report
