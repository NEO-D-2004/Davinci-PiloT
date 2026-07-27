"""
Configuration Loader module for DaVinci PiloT.
Loads environment variables from .env file and provides strongly-typed configuration settings.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class ConfigLoader:
    """Loads environment variables and app configuration."""

    def __init__(self, env_path: Optional[Path] = None) -> None:
        if env_path is None:
            # Default to root directory .env
            env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv()

    @property
    def app_name(self) -> str:
        return os.getenv("APP_NAME", "Davinci PiloT")

    @property
    def app_env(self) -> str:
        return os.getenv("APP_ENV", "development")

    @property
    def log_level(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")

    @property
    def resolve_script_api(self) -> str:
        # Check primary Windows ProgramData location first
        progdata_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
        progfiles_path = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting"
        
        if Path(progdata_path).exists():
            default_path = progdata_path
        else:
            default_path = progfiles_path

        return os.getenv("RESOLVE_SCRIPT_API", default_path)

    @property
    def resolve_script_lib(self) -> str:
        return os.getenv(
            "RESOLVE_SCRIPT_LIB",
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        )

    @property
    def default_ai_provider(self) -> str:
        return os.getenv("DEFAULT_AI_PROVIDER", "nvidia_nim")

    @property
    def nvidia_nim_api_key(self) -> str:
        return os.getenv("NVIDIA_NIM_API_KEY", "")

    @property
    def nvidia_nim_base_url(self) -> str:
        return os.getenv("NVIDIA_NIM_BASE_URL", "https://integrate.api.nvidia.com/v1")

    # 7-Agent Architecture Model Assignments (NVIDIA NIM build.nvidia.com)
    @property
    def model_master_agent(self) -> str:
        return os.getenv("NVIDIA_MODEL_MASTER_AGENT", "GLM-5.2")

    @property
    def model_vision_agent(self) -> str:
        return os.getenv("NVIDIA_MODEL_VISION_AGENT", "MiniMax M3")

    @property
    def model_speech_agent(self) -> str:
        return os.getenv("NVIDIA_MODEL_SPEECH_AGENT", "Nemotron ASR Streaming")

    @property
    def model_ocr_agent(self) -> str:
        return os.getenv("NVIDIA_MODEL_OCR_AGENT", "Nemotron OCR v2")

    @property
    def model_story_agent(self) -> str:
        return os.getenv("NVIDIA_MODEL_STORY_AGENT", "GLM-5.2")

    @property
    def model_editing_planner(self) -> str:
        return os.getenv("NVIDIA_MODEL_EDITING_PLANNER", "Nemotron-3 Ultra 550B")

    # Frame Extraction Strategy
    @property
    def frame_sample_rate(self) -> float:
        return float(os.getenv("FRAME_SAMPLE_RATE", "1.0"))

    @property
    def extract_scene_boundaries(self) -> bool:
        return os.getenv("EXTRACT_SCENE_BOUNDARIES", "True").lower() == "true"


# Global singleton instance
config = ConfigLoader()
