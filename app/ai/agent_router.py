"""
NVIDIA NIM Multi-Agent Router Module.
Routes specific AI tasks to specialized NVIDIA NIM model endpoints.
"""

from typing import Dict, Any
from app.ai.nim_client import NvidiaNimClient
from app.services.logger_service import app_logger


class AgentTaskRole:
    MASTER_PLANNER = "master_planner"  # GLM-5.2: Master Agent, tool calling & workflow planning
    VISION = "vision"                  # MiniMax M3: Video frame & multimodal image understanding
    REASONING = "reasoning"            # Nemotron-3 Ultra 550B: Complex timeline editing decisions
    OCR = "ocr"                        # Nemotron OCR v2: Subtitle, text, slide & screen OCR
    ASR = "asr"                        # Nemotron ASR Streaming: Timestamped speech recognition
    EMBEDDINGS = "embeddings"          # Nemotron Embed 1B: Vector embeddings & semantic retrieval


class AgentRouter:
    """Orchestrates multi-agent routing using NVIDIA NIM microservices."""

    def __init__(self, nim_client: NvidiaNimClient = None) -> None:
        self.client = nim_client or NvidiaNimClient()

    def get_agent_specs(self) -> Dict[str, Dict[str, str]]:
        """Return the multi-agent task-to-model mapping matrix."""
        return {
            AgentTaskRole.MASTER_PLANNER: {
                "model": self.client.get_model_for_role(AgentTaskRole.MASTER_PLANNER),
                "description": "Master Agent & Planning - Long horizon planning, tool calling, workflow orchestration."
            },
            AgentTaskRole.VISION: {
                "model": self.client.get_model_for_role(AgentTaskRole.VISION),
                "description": "Vision Understanding - Multimodal image + text reasoning for video frames."
            },
            AgentTaskRole.REASONING: {
                "model": self.client.get_model_for_role(AgentTaskRole.REASONING),
                "description": "Long Reasoning - Complex editing decisions, timeline planning, high-level logic."
            },
            AgentTaskRole.OCR: {
                "model": self.client.get_model_for_role(AgentTaskRole.OCR),
                "description": "OCR - Multilingual OCR for subtitles, signs, slides, and screen recordings."
            },
            AgentTaskRole.ASR: {
                "model": self.client.get_model_for_role(AgentTaskRole.ASR),
                "description": "Speech Recognition - Timestamped speech-to-text transcription."
            },
            AgentTaskRole.EMBEDDINGS: {
                "model": self.client.get_model_for_role(AgentTaskRole.EMBEDDINGS),
                "description": "Semantic Search - Vector embeddings for retrieving events, transcripts & prior analyses."
            },
        }

    def route_task(self, role: str) -> str:
        """Get the model ID assigned for a given task role."""
        model = self.client.get_model_for_role(role)
        app_logger.debug(f"Routed agent role '{role}' -> NVIDIA NIM model '{model}'")
        return model
