"""
JSON Settings Manager module.
Provides persistent configuration storage (user_settings.json) with default fallbacks and Qt signals for UI synchronization.
"""

import json
from pathlib import Path
from typing import Any, Dict
from PySide6.QtCore import QObject, Signal
from app.services.logger_service import app_logger


DEFAULT_SETTINGS: Dict[str, Any] = {
    "theme": "dark",
    "ai_provider": "gemini",
    "openai_api_key": "",
    "nvidia_nim_api_key": "",
    "gemini_api_key": "",
    "local_llm_url": "http://localhost:11434/v1",
    "resolve_path": r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting",
    "auto_connect_resolve": True,
    "log_level": "INFO",
    "window_geometry": {},
    "recent_projects": [],
}


class SettingsSignalEmitter(QObject):
    """Signals for settings modifications."""
    setting_changed = Signal(str, object)  # (key, new_value)


class SettingsManager:
    """Manages application settings reading/writing to user_settings.json."""

    def __init__(self, settings_file: Path = None) -> None:
        self.signal_emitter = SettingsSignalEmitter()
        if settings_file is None:
            settings_dir = Path(__file__).resolve().parent.parent / "settings"
            settings_dir.mkdir(parents=True, exist_ok=True)
            settings_file = settings_dir / "user_settings.json"
        
        self.settings_file = settings_file
        self._settings: Dict[str, Any] = {}
        self.load_settings()

    def load_settings(self) -> None:
        """Load settings from JSON file or create with defaults if missing."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._settings = {**DEFAULT_SETTINGS, **data}
                    app_logger.info(f"Loaded settings from {self.settings_file}")
            except Exception as e:
                app_logger.error(f"Error loading settings file: {e}. Reverting to defaults.")
                self._settings = DEFAULT_SETTINGS.copy()
        else:
            self._settings = DEFAULT_SETTINGS.copy()
            self.save_settings()

    def save_settings(self) -> None:
        """Save settings dictionary to JSON file."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4)
            app_logger.debug(f"Saved settings to {self.settings_file}")
        except Exception as e:
            app_logger.error(f"Failed to save settings: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve setting by key."""
        return self._settings.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Update setting value, save file, and emit signal."""
        old_val = self._settings.get(key)
        if old_val != value:
            self._settings[key] = value
            self.save_settings()
            self.signal_emitter.setting_changed.emit(key, value)
            app_logger.debug(f"Setting updated: {key} = {value}")

    def get_all(self) -> Dict[str, Any]:
        """Return a copy of all settings."""
        return self._settings.copy()


# Global singleton settings manager
settings_manager = SettingsManager()
