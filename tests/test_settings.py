"""
Unit tests for SettingsManager module.
"""

from pathlib import Path
from app.settings import SettingsManager


def test_settings_manager_load_save(tmp_path: Path):
    test_file = tmp_path / "test_settings.json"
    manager = SettingsManager(settings_file=test_file)

    # Verify defaults
    assert manager.get("theme") == "dark"
    assert manager.get("ai_provider") == "gemini"

    # Modify setting
    manager.set("ai_provider", "nvidia_nim")
    assert manager.get("ai_provider") == "nvidia_nim"

    # Reload from file
    new_manager = SettingsManager(settings_file=test_file)
    assert new_manager.get("ai_provider") == "nvidia_nim"
