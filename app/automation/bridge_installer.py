"""
DaVinci PiloT IPC Bridge Installer.
Deploys DaVinciPiloT_Bridge.py into DaVinci Resolve Fusion Scripts directory
to enable seamless integration for DaVinci Resolve Free and Studio users.
"""

import os
import sys
from pathlib import Path
from app.services.logger_service import app_logger

ROAMING_FUSION_SCRIPTS = Path(os.path.expandvars(r"%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility"))

BRIDGE_SCRIPT_CONTENT = '''# DaVinci PiloT IPC Relay Bridge for DaVinci Resolve (Free & Studio)
# Automatically deployed by DaVinci PiloT Desktop Application

import sys
import os
import json
import urllib.request

print("[DaVinci PiloT Bridge] Connecting to DaVinci PiloT Command Center...")

try:
    # Acquire active Resolve handle inside DaVinci Resolve environment
    if "bmd" in globals():
        resolve_obj = bmd.scriptapp("Resolve")
    else:
        import DaVinciResolveScript as bmd
        resolve_obj = bmd.scriptapp("Resolve")

    if not resolve_obj and "resolve" in globals():
        resolve_obj = globals()["resolve"]

    if resolve_obj:
        pm = resolve_obj.GetProjectManager()
        proj = pm.GetCurrentProject() if pm else None
        proj_name = proj.GetName() if proj else "No Project Open"
        print(f"[DaVinci PiloT Bridge] Connected! Active Project: {proj_name}")
    else:
        print("[DaVinci PiloT Bridge] Error: Could not acquire Resolve handle.")
except Exception as e:
    print(f"[DaVinci PiloT Bridge] Exception: {e}")
'''


def install_resolve_bridge() -> bool:
    """Deploy DaVinciPiloT_Bridge.py into Resolve Utility scripts directory."""
    try:
        if not ROAMING_FUSION_SCRIPTS.exists():
            ROAMING_FUSION_SCRIPTS.mkdir(parents=True, exist_ok=True)

        bridge_file = ROAMING_FUSION_SCRIPTS / "DaVinciPiloT_Bridge.py"
        with open(bridge_file, "w", encoding="utf-8") as f:
            f.write(BRIDGE_SCRIPT_CONTENT)

        app_logger.info(f"Deployed DaVinci PiloT Bridge script to: {bridge_file}")
        return True
    except Exception as e:
        app_logger.warning(f"Could not deploy DaVinci PiloT Bridge script: {e}")
        return False
