"""
Main ViewModel for DaVinci PiloT.
Coordinates app business logic, view state bindings, settings updates, and background service interactions.
"""

from PySide6.QtCore import QObject, Signal
from app.services.logger_service import app_logger
from app.settings import settings_manager
from app.database import db_manager


class MainViewModel(QObject):
    """Main ViewModel managing application state."""

    # View signals
    connection_state_changed = Signal(bool)
    status_message_changed = Signal(str)
    notification_emitted = Signal(str, str)  # (type, message)
    ai_provider_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._is_resolve_connected = False
        self._ai_provider = settings_manager.get("ai_provider", "gemini")
        
        # Subscribe to settings changes
        settings_manager.signal_emitter.setting_changed.connect(self._on_setting_changed)

    @property
    def is_resolve_connected(self) -> bool:
        return self._is_resolve_connected

    @property
    def ai_provider(self) -> str:
        return self._ai_provider

    def toggle_resolve_connection(self) -> None:
        """Toggle DaVinci Resolve connection state (Bridge to Milestone 2)."""
        self._is_resolve_connected = not self._is_resolve_connected
        state_str = "Connected" if self._is_resolve_connected else "Disconnected"
        app_logger.info(f"DaVinci Resolve connection toggled: {state_str}")
        
        db_manager.log_activity(
            level="INFO",
            category="RESOLVE_CONN",
            message=f"Resolve connection toggled to {state_str}"
        )
        
        self.connection_state_changed.emit(self._is_resolve_connected)
        self.status_message_changed.emit(f"DaVinci Resolve {state_str}")
        
        n_type = "success" if self._is_resolve_connected else "warning"
        self.notification_emitted.emit(n_type, f"DaVinci Resolve is now {state_str}")

    def _on_setting_changed(self, key: str, value: object) -> None:
        """Handle settings changes."""
        if key == "ai_provider":
            self._ai_provider = str(value)
            self.ai_provider_changed.emit(self._ai_provider)
            self.notification_emitted.emit("info", f"AI Provider changed to {self._ai_provider}")
