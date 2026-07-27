"""
NVIDIA NIM Client Module for DaVinci PiloT.
Interacts with build.nvidia.com free endpoints using OpenAI-compatible API protocol.
Supports 7 specialized agent models: GLM-5.2, MiniMax M3, Nemotron ASR, Nemotron OCR v2, Nemotron-3 Ultra 550B, and Nemotron Embed 1B.
"""

from typing import Dict, Any, Optional
from app.settings import settings_manager
from app.services.logger_service import app_logger


class NvidiaNimClient:
    """Client wrapper for NVIDIA NIM microservices (build.nvidia.com)."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key or settings_manager.get("nvidia_nim_api_key", "")
        self.base_url = base_url or settings_manager.get(
            "nvidia_nim_base_url", "https://integrate.api.nvidia.com/v1"
        )
        self.models = settings_manager.get("agent_matrix", {
            "master_agent": "GLM-5.2",
            "vision_agent": "MiniMax M3",
            "speech_agent": "Nemotron ASR Streaming",
            "ocr_agent": "Nemotron OCR v2",
            "story_agent": "GLM-5.2",
            "editing_planner": "Nemotron-3 Ultra 550B",
            "resolve_agent": "Deterministic DaVinci API Translator"
        })

    def is_configured(self) -> bool:
        """Check if NVIDIA NIM API Key is set."""
        return bool(self.api_key and self.api_key.strip())

    def get_model_for_role(self, role: str) -> str:
        """Return designated NVIDIA NIM model for specific agent role."""
        return self.models.get(role.lower(), self.models.get("master_agent", "GLM-5.2"))

    def get_summary(self) -> Dict[str, Any]:
        """Return client state summary."""
        return {
            "provider": "NVIDIA NIM (build.nvidia.com)",
            "configured": self.is_configured(),
            "base_url": self.base_url,
            "models": self.models
        }
