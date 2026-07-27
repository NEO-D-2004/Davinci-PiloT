"""
Unit tests for ConfigLoader module.
"""

from app.config import ConfigLoader


def test_config_loader_defaults():
    loader = ConfigLoader()
    assert loader.app_name == "Davinci PiloT"
    assert loader.app_env in ["development", "production", "test"]
    assert isinstance(loader.resolve_script_api, str)
    assert isinstance(loader.resolve_script_lib, str)
