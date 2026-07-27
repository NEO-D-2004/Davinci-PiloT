"""
General-Purpose AI Video Editing Pipeline for DaVinci PiloT.
Orchestrates the 9-stage content-agnostic video processing pipeline across all 7 specialized agents.
"""

from typing import Dict, Any, List
from app.ai.agent_router import AgentRouter, AgentTaskRole
from app.ai.frame_sampler import FrameSampler
from app.services.logger_service import app_logger


class PipelineStage:
    STAGE_1_FRAME_EXTRACTION = "1_Frame_Extraction"
    STAGE_2_SPEECH_RECOGNITION = "2_Speech_Recognition_ASR"
    STAGE_3_OCR_RECOGNITION = "3_OCR_Recognition"
    STAGE_4_VISION_UNDERSTANDING = "4_Vision_Understanding"
    STAGE_5_SCENE_DETECTION = "5_Scene_Detection"
    STAGE_6_STORY_UNDERSTANDING = "6_Story_Understanding"
    STAGE_7_EDITING_PLANNER = "7_Editing_Planner"
    STAGE_8_TIMELINE_JSON = "8_Timeline_JSON_Generation"
    STAGE_9_RESOLVE_EXECUTION = "9_DaVinci_Resolve_Execution"


class GeneralEditingPipeline:
    """Master Multi-Agent Pipeline for automated video editing."""

    def __init__(self, router: AgentRouter = None, sampler: FrameSampler = None) -> None:
        self.router = router or AgentRouter()
        self.sampler = sampler or FrameSampler()

    def get_pipeline_stages(self) -> List[Dict[str, str]]:
        """Return the 9 pipeline stages with assigned agent roles and models."""
        matrix = self.router.get_agent_matrix()
        return [
            {
                "stage": PipelineStage.STAGE_1_FRAME_EXTRACTION,
                "name": "Frame & Audio Extraction",
                "agent": "FFmpeg Engine",
                "model": f"Sample Rate: {self.sampler.sample_rate_fps} FPS",
                "description": "Extracts sampled frames & audio stream without sending raw long video to LLMs."
            },
            {
                "stage": PipelineStage.STAGE_2_SPEECH_RECOGNITION,
                "name": "Speech Recognition (ASR)",
                "agent": matrix[AgentTaskRole.SPEECH_AGENT]["title"],
                "model": matrix[AgentTaskRole.SPEECH_AGENT]["model"],
                "description": "Converts audio to timestamped text, speaker IDs, filler word detection & pauses."
            },
            {
                "stage": PipelineStage.STAGE_3_OCR_RECOGNITION,
                "name": "OCR Recognition",
                "agent": matrix[AgentTaskRole.OCR_AGENT]["title"],
                "model": matrix[AgentTaskRole.OCR_AGENT]["model"],
                "description": "Extracts slides, code snippets, subtitles, UI text & labels from frames."
            },
            {
                "stage": PipelineStage.STAGE_4_VISION_UNDERSTANDING,
                "name": "Vision Understanding",
                "agent": matrix[AgentTaskRole.VISION_AGENT]["title"],
                "model": matrix[AgentTaskRole.VISION_AGENT]["model"],
                "description": "Analyzes sampled keyframes for scenes, actions, emotions & camera movements."
            },
            {
                "stage": PipelineStage.STAGE_5_SCENE_DETECTION,
                "name": "Scene Boundary Detection",
                "agent": "Shot Boundary Detector",
                "model": "Keyframe Indexer",
                "description": "Groups frames into coherent visual scene blocks."
            },
            {
                "stage": PipelineStage.STAGE_6_STORY_UNDERSTANDING,
                "name": "Story Understanding",
                "agent": matrix[AgentTaskRole.STORY_AGENT]["title"],
                "model": matrix[AgentTaskRole.STORY_AGENT]["model"],
                "description": "Synthesizes {speech, scene, emotion, ocr} data into narrative arcs & cut recommendations."
            },
            {
                "stage": PipelineStage.STAGE_7_EDITING_PLANNER,
                "name": "Editing Planner",
                "agent": matrix[AgentTaskRole.EDITING_PLANNER]["title"],
                "model": matrix[AgentTaskRole.EDITING_PLANNER]["model"],
                "description": "Converts story synthesis into a structured timeline decision plan."
            },
            {
                "stage": PipelineStage.STAGE_8_TIMELINE_JSON,
                "name": "Timeline JSON Generation",
                "agent": matrix[AgentTaskRole.MASTER_AGENT]["title"],
                "model": matrix[AgentTaskRole.MASTER_AGENT]["model"],
                "description": "Compiles decisions into final execution schema {clip, start, end, keep, effect}."
            },
            {
                "stage": PipelineStage.STAGE_9_RESOLVE_EXECUTION,
                "name": "DaVinci Resolve Execution",
                "agent": matrix[AgentTaskRole.RESOLVE_AGENT]["title"],
                "model": matrix[AgentTaskRole.RESOLVE_AGENT]["model"],
                "description": "Executes cuts, trims, transitions, and timeline edits via DaVinci Scripting API."
            },
        ]
