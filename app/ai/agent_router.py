"""
NVIDIA NIM Multi-Agent Router Module.
Defines the 7 specialized agents and routes tasks across the general-purpose video editing pipeline.
"""

from typing import Dict, Any, List
from app.ai.nim_client import NvidiaNimClient
from app.services.logger_service import app_logger


class AgentTaskRole:
    MASTER_AGENT = "master_agent"          # GLM-5.2: User request understanding, workflow orchestration, merging plan, retries
    VISION_AGENT = "vision_agent"          # MiniMax M3: Sampled frame understanding, scene description, person/action detection, emotions
    SPEECH_AGENT = "speech_agent"          # Nemotron ASR Streaming: Timestamped audio transcript, speaker diarization, filler word detection
    OCR_AGENT = "ocr_agent"                # Nemotron OCR v2: On-screen slides, code, subtitles, UI text, labels & signs
    STORY_AGENT = "story_agent"            # GLM-5.2 / Composite: Consumes structured multimodal events, extracts narrative arc & cut candidates
    EDITING_PLANNER = "editing_planner"    # Nemotron-3 Ultra 550B: Converts story understanding into structured Timeline Action JSON
    RESOLVE_AGENT = "resolve_agent"        # Deterministic Translator: Converts Timeline Action JSON into official DaVinci Resolve Scripting API calls


class AgentRouter:
    """Orchestrates multi-agent routing using 7 specialized agent roles."""

    def __init__(self, nim_client: NvidiaNimClient = None) -> None:
        self.client = nim_client or NvidiaNimClient()

    def get_agent_matrix(self) -> Dict[str, Dict[str, str]]:
        """Return full 7-Agent matrix details."""
        return {
            AgentTaskRole.MASTER_AGENT: {
                "model": self.client.get_model_for_role(AgentTaskRole.MASTER_AGENT),
                "title": "Master Agent",
                "description": "Understand user prompt, invoke specialists, merge plans, manage retries & error handling."
            },
            AgentTaskRole.VISION_AGENT: {
                "model": self.client.get_model_for_role(AgentTaskRole.VISION_AGENT),
                "title": "Vision Agent",
                "description": "Analyzes sampled video frames for scene descriptions, person/action detection, camera angles & emotions."
            },
            AgentTaskRole.SPEECH_AGENT: {
                "model": self.client.get_model_for_role(AgentTaskRole.SPEECH_AGENT),
                "title": "Speech Agent (ASR)",
                "description": "Converts audio to timestamped text, speaker diarization, filler word detection & transcript segments."
            },
            AgentTaskRole.OCR_AGENT: {
                "model": self.client.get_model_for_role(AgentTaskRole.OCR_AGENT),
                "title": "OCR Agent",
                "description": "Extracts on-screen presentation slides, code, subtitles, UI text, labels & signs."
            },
            AgentTaskRole.STORY_AGENT: {
                "model": self.client.get_model_for_role(AgentTaskRole.STORY_AGENT),
                "title": "Story Understanding Agent",
                "description": "Synthesizes multi-modal data {speech, scene, emotion, ocr} into narrative arcs and cut recommendations."
            },
            AgentTaskRole.EDITING_PLANNER: {
                "model": self.client.get_model_for_role(AgentTaskRole.EDITING_PLANNER),
                "title": "Editing Planner Agent",
                "description": "Converts story understanding into structured Timeline Action JSON {clip, start, end, keep, effect}."
            },
            AgentTaskRole.RESOLVE_AGENT: {
                "model": self.client.get_model_for_role(AgentTaskRole.RESOLVE_AGENT),
                "title": "Resolve API Agent",
                "description": "Deterministic translator mapping Timeline Action JSON directly into official DaVinci Resolve API calls."
            },
        }

    def route_task(self, role: str) -> str:
        """Get the model ID assigned for a given agent role."""
        model = self.client.get_model_for_role(role)
        app_logger.debug(f"Routed agent role '{role}' -> NVIDIA NIM model '{model}'")
        return model
