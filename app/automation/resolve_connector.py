"""
DaVinci Resolve Scripting API Connector Module.
Loads fusionscript.dll and initializes the official DaVinciResolveScript scripting handle.
Ref: https://extremraym.com/cloud/resolve-scripting-doc/#davinci-resolve-api
"""

import sys
import os
import sysconfig
from pathlib import Path
from typing import Optional, Tuple, Any
from app.config import config
from app.services.logger_service import app_logger


class ResolveConnector:
    """Handles dynamic loading of DaVinci Resolve Scripting API library."""

    def __init__(self) -> None:
        self._resolve_app: Optional[Any] = None

    @property
    def script_api_path(self) -> str:
        from app.settings import settings_manager
        return settings_manager.get("resolve_path", config.resolve_script_api)

    def detect_resolve_process(self) -> bool:
        """Check if DaVinci Resolve process is running on Windows."""
        try:
            import subprocess
            cmd = 'tasklist /FI "IMAGENAME eq Resolve.exe" /NH'
            output = subprocess.check_output(cmd, shell=True, text=True, errors="ignore")
            return "Resolve.exe" in output
        except Exception as e:
            app_logger.warning(f"Error checking Resolve process: {e}")
            return False

    def load_script_module(self) -> Optional[Any]:
        """Dynamically import DaVinciResolveScript module."""
        try:
            # 1. Setup environment paths for Blackmagic Scripting API
            base_script_path = Path(self.script_api_path)
            modules_path = base_script_path / "Modules"

            if modules_path.exists() and str(modules_path) not in sys.path:
                sys.path.append(str(modules_path))

            # Set environment variables expected by fusionscript
            os.environ["RESOLVE_SCRIPT_API"] = str(base_script_path)
            os.environ["RESOLVE_SCRIPT_LIB"] = str(
                Path(config.resolve_script_lib)
            )

            # 2. Try importing official DaVinciResolveScript module
            import DaVinciResolveScript as bmd
            return bmd
        except ImportError:
            app_logger.debug("DaVinciResolveScript module not found via standard import. Attempting fallback CTypes loader...")
            return self._load_via_ctypes()
        except Exception as e:
            app_logger.error(f"Failed to load DaVinciResolveScript: {e}")
            return None

    def _load_via_ctypes(self) -> Optional[Any]:
        """Fallback dynamic loader for fusionscript.dll on Windows."""
        try:
            import ctypes
            dll_path = Path(config.resolve_script_lib)
            if not dll_path.exists():
                app_logger.error(f"fusionscript.dll not found at path: {dll_path}")
                return None

            # Load fusionscript DLL
            fusion_dll = ctypes.PyDLL(str(dll_path))
            if hasattr(fusion_dll, "GetFusion"):
                app_logger.info(f"Successfully loaded fusionscript DLL from {dll_path}")

            # Re-try module import after DLL load
            import DaVinciResolveScript as bmd
            return bmd
        except Exception as e:
            app_logger.error(f"CTypes loader failed: {e}")
            return None

    def connect(self) -> Tuple[Optional[Any], Optional[str]]:
        """Connect to DaVinci Resolve instance and return (resolve_handle, error_message)."""
        # Step 1: Check process
        if not self.detect_resolve_process():
            msg = "DaVinci Resolve is not running. Please launch DaVinci Resolve on your system."
            app_logger.warning(msg)
            return None, msg

        # Step 2: Load API Module
        bmd = self.load_script_module()
        if not bmd:
            msg = f"Failed to load DaVinci Resolve Scripting API from {self.script_api_path}. Verify scripting installation."
            app_logger.error(msg)
            return None, msg

        # Step 3: Acquire Resolve Application Object
        try:
            resolve = bmd.scriptapp("Resolve")
            if not resolve:
                msg = "Connected to Scripting API, but DaVinci Resolve application instance returned None. Ensure a project is open in Resolve."
                app_logger.warning(msg)
                return None, msg

            self._resolve_app = resolve
            app_logger.info("Successfully connected to DaVinci Resolve Scripting API!")
            return resolve, None
        except Exception as e:
            msg = f"Error calling bmd.scriptapp('Resolve'): {e}"
            app_logger.error(msg)
            return None, msg

    def disconnect(self) -> None:
        """Drop Resolve API handle."""
        self._resolve_app = None
        app_logger.info("Disconnected from DaVinci Resolve API.")
