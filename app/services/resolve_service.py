"""
DaVinci Resolve Service Module.
Service layer orchestrating DaVinci Resolve connection, active project/timeline queries, and state notifications.
"""

from typing import Optional, Tuple
from app.automation.resolve_connector import ResolveConnector
from app.automation.resolve_api import ResolveApiWrapper
from app.models.resolve_models import ResolveState
from app.services.logger_service import app_logger


class ResolveService:
    """Central service managing DaVinci Resolve integration."""

    def __init__(self) -> None:
        self.connector = ResolveConnector()
        self.api = ResolveApiWrapper()
        self._current_state = ResolveState(is_connected=False)

    @property
    def is_connected(self) -> bool:
        return self._current_state.is_connected

    @property
    def current_state(self) -> ResolveState:
        return self._current_state

    def connect(self) -> Tuple[bool, str]:
        """Attempt connection to DaVinci Resolve."""
        app_logger.info("Attempting connection to DaVinci Resolve...")
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
            self._current_state = ResolveState(is_connected=False, error_message=msg)
            return False, msg

    def refresh_state(self) -> ResolveState:
        """Poll and update current Resolve state if connected."""
        if self._current_state.is_connected and self.connector.detect_resolve_process():
            self._current_state = self.api.query_full_state()
        else:
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
