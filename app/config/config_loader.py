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
        return os.getenv(
            "RESOLVE_SCRIPT_API",
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting"
        )

    @property
    def resolve_script_lib(self) -> str:
        return os.getenv(
            "RESOLVE_SCRIPT_LIB",
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        )

    @property
    def default_ai_provider(self) -> str:
        return os.getenv("DEFAULT_AI_PROVIDER", "gemini")

# Global singleton instance
config = ConfigLoader()
