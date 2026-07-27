"""
DaVinci Resolve Scripting API Connector Module.
Loads fusionscript.dll and initializes the official DaVinciResolveScript scripting handle with Python 3.13 compatibility.
Ref: https://extremraym.com/cloud/resolve-scripting-doc/#davinci-resolve-api
"""

import sys
import os
import types
import ctypes
from pathlib import Path
from typing import Optional, Tuple, Any, List
from app.config import config
from app.services.logger_service import app_logger


CANDIDATE_SCRIPT_PATHS: List[str] = [
    r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting",
    r"C:\Program Files\Blackmagic Design\DaVinci Resolve\Developer\Scripting",
]

CANDIDATE_DLL_PATHS: List[str] = [
    r"C:\Program Files\Blackmagic Design\DaVinci Resolve",
    r"C:\Program Files (x86)\Blackmagic Design\DaVinci Resolve",
]


class ResolveConnector:
    """Handles dynamic loading of DaVinci Resolve Scripting API library."""

    def __init__(self) -> None:
        self._resolve_app: Optional[Any] = None

    @property
    def script_api_path(self) -> str:
        from app.settings import settings_manager
        configured_path = settings_manager.get("resolve_path")
        if configured_path and Path(configured_path).exists():
            return configured_path

        for path_str in CANDIDATE_SCRIPT_PATHS:
            if Path(path_str).exists():
                return path_str

        return config.resolve_script_api

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

    def _setup_dll_environment(self) -> Optional[Path]:
        """Add Resolve installation directory to Windows DLL search path."""
        found_dll_dir: Optional[Path] = None

        for dll_dir in CANDIDATE_DLL_PATHS:
            p_dir = Path(dll_dir)
            if p_dir.exists():
                found_dll_dir = p_dir
                if str(p_dir) not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = str(p_dir) + os.pathsep + os.environ.get("PATH", "")

                if hasattr(os, "add_dll_directory"):
                    try:
                        os.add_dll_directory(str(p_dir))
                    except Exception:
                        pass

                dll_file = p_dir / "fusionscript.dll"
                if dll_file.exists():
                    os.environ["RESOLVE_SCRIPT_LIB"] = str(dll_file)
                break

        return found_dll_dir

    def load_script_module(self) -> Optional[Any]:
        """Dynamically import DaVinciResolveScript module with Python 3.13 compatibility bridge."""
        try:
            dll_dir = self._setup_dll_environment()

            base_script_path = Path(self.script_api_path)
            modules_path = base_script_path / "Modules"

            if not modules_path.exists():
                for candidate in CANDIDATE_SCRIPT_PATHS:
                    cand_modules = Path(candidate) / "Modules"
                    if cand_modules.exists():
                        base_script_path = Path(candidate)
                        modules_path = cand_modules
                        break

            if modules_path.exists() and str(modules_path) not in sys.path:
                sys.path.append(str(modules_path))

            os.environ["RESOLVE_SCRIPT_API"] = str(base_script_path)

            # Ensure fusionscript module bridge is safely initialized in sys.modules
            if "fusionscript" not in sys.modules:
                fusion_mod = types.ModuleType("fusionscript")
                
                # Load fusionscript.dll via CTypes
                if dll_dir and (dll_dir / "fusionscript.dll").exists():
                    try:
                        ctypes.cdll.LoadLibrary(str(dll_dir / "fusionscript.dll"))
                        app_logger.info(f"Loaded fusionscript.dll via CDLL from {dll_dir}")
                    except Exception as err:
                        app_logger.debug(f"CDLL load note: {err}")

                def scriptapp_wrapper(app_name, *args):
                    # Try importing bmd / DaVinciResolveScript if available
                    try:
                        if hasattr(sys.modules.get("DaVinciResolveScript"), "scriptapp"):
                            return sys.modules["DaVinciResolveScript"].scriptapp(app_name, *args)
                    except Exception:
                        pass
                    return None

                fusion_mod.scriptapp = scriptapp_wrapper
                sys.modules["fusionscript"] = fusion_mod

            app_logger.debug(f"Loading DaVinciResolveScript from: {modules_path}")
            import DaVinciResolveScript as bmd
            return bmd
        except Exception as e:
            app_logger.error(f"Failed to load DaVinciResolveScript: {e}")
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
            msg = (
                f"Failed to load DaVinci Resolve Scripting API module. "
                f"Searched paths: {CANDIDATE_SCRIPT_PATHS}. Verify DaVinci Resolve installation."
            )
            app_logger.error(msg)
            return None, msg

        # Step 3: Acquire Resolve Application Object
        try:
            resolve = None
            if hasattr(bmd, "scriptapp"):
                resolve = bmd.scriptapp("Resolve")

            if not resolve:
                msg = (
                    "DaVinci Resolve is running, but scriptapp('Resolve') returned None. "
                    "In DaVinci Resolve, go to Preferences (Ctrl+,) -> System -> General and ensure "
                    "'External scripting using' is set to 'Local' or 'Network'."
                )
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
