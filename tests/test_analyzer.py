"""
Unit tests for Milestone 5 NVIDIA NIM Multi-Agent Vision & Audio Analyzer models, engines, and view components.
"""

from app.models.analyzer_models import (
    TranscriptSegment, SilenceGap, VisualFrameInsight, SmartCutProposal, AnalysisReport
)
from app.ai.analyzer_engine import AudioAnalyzer, VisionAnalyzer, format_seconds_to_tc
from app.ai.multi_agent_pipeline import MultiAgentAnalyzer
from app.ui.views.analyzer_view import AnalyzerView


def test_analyzer_models():
    seg = TranscriptSegment(
        segment_id="s1",
        start_sec=1.0,
        end_sec=5.0,
        text="Hello world of DaVinci PiloT.",
        confidence=0.99
    )
    assert seg.segment_id == "s1"
    assert seg.to_dict()["text"] == "Hello world of DaVinci PiloT."

    gap = SilenceGap(
        gap_id="g1",
        start_sec=5.0,
        end_sec=8.5,
        duration_sec=3.5,
        recommended_action="Ripple Cut Silence"
    )
    assert gap.duration_sec == 3.5

    insight = VisualFrameInsight(
        frame_idx=1,
        timestamp_sec=2.0,
        scene_description="Presenter at desk with microphone."
    )
    assert insight.frame_idx == 1

    cut = SmartCutProposal(
        cut_id="c1",
        clip_name="Demo.mp4",
        start_sec=5.0,
        end_sec=8.5,
        cut_type="Silence",
        reason="Remove long pause",
        priority="HIGH"
    )
    assert cut.priority == "HIGH"

    report = AnalysisReport(
        asset_name="Demo.mp4",
        total_duration_sec=60.0,
        segments=[seg],
        silence_gaps=[gap],
        frame_insights=[insight],
        cut_proposals=[cut]
    )

    assert report.total_silence_time == 3.5
    assert len(report.segments) == 1
    assert len(report.cut_proposals) == 1
    assert report.to_dict()["asset_name"] == "Demo.mp4"


def test_audio_analyzer_engine():
    audio_engine = AudioAnalyzer()
    segments, gaps = audio_engine.analyze_speech_and_silence("test_audio.wav", duration_sec=40.0)

    assert len(segments) > 0
    assert len(gaps) > 0
    assert gaps[0].duration_sec > 1.0


def test_vision_analyzer_engine():
    vision_engine = VisionAnalyzer()
    insights = vision_engine.analyze_video_keyframes("test_video.mp4", sample_interval_sec=5.0)

    assert len(insights) > 0
    assert insights[0].quality_score > 5.0


def test_multi_agent_pipeline():
    pipeline = MultiAgentAnalyzer()
    report = pipeline.run_full_analysis("Sample_Asset.mp4", "Sample_Asset.mp4", duration_sec=45.0)

    assert report.asset_name == "Sample_Asset.mp4"
    assert len(report.segments) > 0
    assert len(report.cut_proposals) > 0


def test_analyzer_view_instantiation(qtbot):
    view = AnalyzerView()
    qtbot.addWidget(view)

    assert "DaVinci Resolve" in view.summary_card.text()
    assert view.transcript_table.rowCount() == 0

    # Test displaying report
    report = AnalysisReport(
        asset_name="Interview.mp4",
        total_duration_sec=30.0,
        segments=[TranscriptSegment(segment_id="s1", start_sec=0, end_sec=5, text="Testing transcript text.")],
        cut_proposals=[SmartCutProposal(cut_id="c1", start_sec=5, end_sec=8, cut_type="Silence")]
    )

    view.display_report(report)
    assert "Interview.mp4" in view.summary_card.text()
    assert view.transcript_table.rowCount() == 1
    assert view.cuts_table.rowCount() == 1
