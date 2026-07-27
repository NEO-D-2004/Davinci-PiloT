"""
DaVinci Resolve Service Module.
Service layer orchestrating DaVinci Resolve connection, active project/timeline queries, and state notifications.
"""

from typing import Optional, Tuple
from app.automation.resolve_connector import ResolveConnector
from app.automation.resolve_api import ResolveApiWrapper
from app.automation.bridge_server import start_bridge_server
from app.models.resolve_models import ResolveState
from app.services.logger_service import app_logger


class ResolveService:
    """Central service managing DaVinci Resolve integration."""

    def __init__(self) -> None:
        self.connector = ResolveConnector()
        self.api = ResolveApiWrapper()
        self._current_state = ResolveState(is_connected=False)
        # Start local bridge HTTP server to listen for Resolve 21 Free/Studio payloads
        start_bridge_server(self._on_bridge_state_received)

    def _on_bridge_state_received(self, state: ResolveState) -> None:
        """Callback invoked when state payload is received from DaVinciPiloT_Bridge."""
        self._current_state = state
        app_logger.info(f"Updated ResolveState from Bridge: Project='{state.project.name}' (Connected={state.is_connected})")

    @property
    def is_connected(self) -> bool:
        return self._current_state.is_connected

    @property
    def current_state(self) -> ResolveState:
        return self._current_state

    def connect(self) -> Tuple[bool, str]:
        """Attempt connection to DaVinci Resolve."""
        app_logger.info("Attempting connection to DaVinci Resolve...")
        
        # 1. First check if we already received live state from Bridge script
        if self._current_state.is_connected:
            return True, f"Connected to {self._current_state.product_name} ({self._current_state.project.name})"

        # 2. Try direct IPC handle
        handle, err = self.connector.connect()

        if handle:
            self.api.set_handle(handle)
            self._current_state = self.api.query_full_state()
            app_logger.info(
                f"Connected to {self._current_state.product_name} v{self._current_state.resolve_version}. "
                f"Project: '{self._current_state.project.name}'"
            )
            return True, f"Connected to {self._current_state.product_name} ({self._current_state.project.name})"
        else:
            msg = err or "Failed to connect to DaVinci Resolve."
            # If not connected yet, keep last error message
            if not self._current_state.is_connected:
                self._current_state.error_message = msg
            return False, msg

    def refresh_state(self) -> ResolveState:
        """Poll and update current Resolve state if connected."""
        if self._current_state.is_connected and self.connector.detect_resolve_process():
            if self.api._resolve_handle:
                self._current_state = self.api.query_full_state()
        else:
            if not self._current_state.is_connected:
                self._current_state = ResolveState(
                    is_connected=False,
                    error_message="DaVinci Resolve process is not running or disconnected."
                )
        return self._current_state

    def disconnect(self) -> None:
        """Disconnect from DaVinci Resolve."""
        self.connector.disconnect()
        self.api.set_handle(None)
        self._current_state = ResolveState(is_connected=False)
        app_logger.info("ResolveService disconnected.")


# Global singleton service
resolve_service = ResolveService()
