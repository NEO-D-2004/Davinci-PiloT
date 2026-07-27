"""
NVIDIA NIM Client Module for DaVinci PiloT.
Interacts with build.nvidia.com free endpoints using OpenAI-compatible API protocol.
Supports specialized models: GLM-5.2, MiniMax M3, Nemotron-3 Ultra, Nemotron OCR v2, Nemotron ASR, and Nemotron Embed.
"""

from typing import Dict, Any, Optional, List
from app.settings import settings_manager
from app.services.logger_service import app_logger


class NvidiaNimClient:
    """Client wrapper for NVIDIA NIM microservices (build.nvidia.com)."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None) -> None:
        self.api_key = api_key or settings_manager.get("nvidia_nim_api_key", "")
        self.base_url = base_url or settings_manager.get(
            "nvidia_nim_base_url", "https://integrate.api.nvidia.com/v1"
        )
        self.models = settings_manager.get("nim_models", {
            "master_planner": "GLM-5.2",
            "vision": "MiniMax M3",
            "reasoning": "Nemotron-3 Ultra 550B",
            "ocr": "Nemotron OCR v2",
            "asr": "Nemotron ASR Streaming",
            "embeddings": "Nemotron Embed 1B"
        })

    def is_configured(self) -> bool:
        """Check if NVIDIA NIM API Key is set."""
        return bool(self.api_key and self.api_key.strip())

    def get_model_for_role(self, role: str) -> str:
        """Return designated NVIDIA NIM model for specific agent task role."""
        return self.models.get(role.lower(), self.models.get("master_planner", "GLM-5.2"))

    def get_summary(self) -> Dict[str, Any]:
        """Return client state summary."""
        return {
            "provider": "NVIDIA NIM (build.nvidia.com)",
            "configured": self.is_configured(),
            "base_url": self.base_url,
            "models": self.models
        }
