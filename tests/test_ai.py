"""
Unit tests for 7-Agent Architecture, Frame Sampler, and General-Purpose Pipeline.
"""

from app.ai import (
    NvidiaNimClient, AgentRouter, AgentTaskRole,
    FrameSampler, GeneralEditingPipeline, PipelineStage
)


def test_nvidia_nim_client_7_agents():
    client = NvidiaNimClient()
    assert client.get_model_for_role("master_agent") == "GLM-5.2"
    assert client.get_model_for_role("vision_agent") == "MiniMax M3"
    assert client.get_model_for_role("speech_agent") == "Nemotron ASR Streaming"
    assert client.get_model_for_role("ocr_agent") == "Nemotron OCR v2"
    assert client.get_model_for_role("story_agent") == "GLM-5.2"
    assert client.get_model_for_role("editing_planner") == "Nemotron-3 Ultra 550B"


def test_agent_router_matrix():
    router = AgentRouter()
    matrix = router.get_agent_matrix()
    
    assert len(matrix) == 7
    assert matrix[AgentTaskRole.MASTER_AGENT]["model"] == "GLM-5.2"
    assert matrix[AgentTaskRole.VISION_AGENT]["model"] == "MiniMax M3"
    assert matrix[AgentTaskRole.SPEECH_AGENT]["model"] == "Nemotron ASR Streaming"
    assert matrix[AgentTaskRole.OCR_AGENT]["model"] == "Nemotron OCR v2"
    assert matrix[AgentTaskRole.STORY_AGENT]["model"] == "GLM-5.2"
    assert matrix[AgentTaskRole.EDITING_PLANNER]["model"] == "Nemotron-3 Ultra 550B"
    assert matrix[AgentTaskRole.RESOLVE_AGENT]["model"] == "Deterministic DaVinci API Translator"


def test_frame_sampler():
    sampler = FrameSampler(sample_rate_fps=1.0, detect_scene_changes=True)
    manifest = sampler.prepare_sampling_manifest("sample_video.mp4")
    
    assert manifest["video_name"] == "sample_video.mp4"
    assert manifest["sample_rate_fps"] == 1.0
    assert manifest["scene_detection_enabled"] is True


def test_general_editing_pipeline():
    pipeline = GeneralEditingPipeline()
    stages = pipeline.get_pipeline_stages()
    
    assert len(stages) == 9
    assert stages[0]["stage"] == PipelineStage.STAGE_1_FRAME_EXTRACTION
    assert stages[8]["stage"] == PipelineStage.STAGE_9_RESOLVE_EXECUTION
