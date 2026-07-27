"""
Main ViewModel for DaVinci PiloT.
Coordinates app business logic, view state bindings, settings updates, and background service interactions off the main UI thread.
"""

from typing import Optional
from PySide6.QtCore import QObject, Signal, QThread
from app.services.logger_service import app_logger
from app.services.resolve_service import resolve_service
from app.settings import settings_manager
from app.database import db_manager
from app.models.resolve_models import ResolveState


class ResolveConnectWorker(QThread):
    """Background worker for asynchronous DaVinci Resolve connection handshakes."""

    connection_finished = Signal(bool, str, object)  # (success, message, resolve_state)

    def run(self) -> None:
        try:
            success, message = resolve_service.connect()
            state = resolve_service.current_state
            self.connection_finished.emit(success, message, state)
        except Exception as e:
            self.connection_finished.emit(False, str(e), ResolveState(is_connected=False))


class MainViewModel(QObject):
    """Main ViewModel managing application state."""

    # View signals
    connection_state_changed = Signal(bool)
    resolve_state_updated = Signal(object)  # ResolveState
    status_message_changed = Signal(str)
    notification_emitted = Signal(str, str)  # (type, message)
    ai_provider_changed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._is_resolve_connected = False
        self._ai_provider = settings_manager.get("ai_provider", "nvidia_nim")
        self._resolve_state = ResolveState(is_connected=False)
        self._connect_worker: Optional[ResolveConnectWorker] = None

        # Subscribe to settings changes
        settings_manager.signal_emitter.setting_changed.connect(self._on_setting_changed)

        # Automatically listen for live state from DaVinciPiloT_Bridge in Resolve
        resolve_service.state_listeners.append(self._on_bridge_auto_connect)

    @property
    def is_resolve_connected(self) -> bool:
        return self._is_resolve_connected

    @property
    def ai_provider(self) -> str:
        return self._ai_provider

    @property
    def resolve_state(self) -> ResolveState:
        return self._resolve_state

    def _on_bridge_auto_connect(self, state: ResolveState) -> None:
        """Invoked automatically when DaVinciPiloT_Bridge payload is received from Resolve."""
        self._is_resolve_connected = state.is_connected
        self._resolve_state = state

        # Emit PySide6 signals to UI on main thread
        self.connection_state_changed.emit(state.is_connected)
        self.resolve_state_updated.emit(state)

        if state.is_connected:
            app_logger.info(f"Auto-connected via Bridge: Project='{state.project.name}'")
            db_manager.log_activity(
                level="INFO",
                category="RESOLVE_CONN",
                message=f"Auto-connected to DaVinci Resolve via Bridge ({state.project.name})"
            )
            self.status_message_changed.emit(f"Connected to DaVinci Resolve - {state.project.name}")
            self.notification_emitted.emit("success", f"Auto-connected to DaVinci Resolve! Project: '{state.project.name}'")
        else:
            self.status_message_changed.emit("DaVinci Resolve Disconnected")

    def toggle_resolve_connection(self) -> None:
        """Asynchronously connect or disconnect from DaVinci Resolve."""
        if self._is_resolve_connected:
            self._disconnect_resolve()
        else:
            self._connect_resolve_async()

    def _connect_resolve_async(self) -> None:
        """Launch background thread for Resolve connection handshake."""
        self.status_message_changed.emit("Connecting to DaVinci Resolve...")
        self.notification_emitted.emit("info", "Detecting DaVinci Resolve process and API handle...")

        self._connect_worker = ResolveConnectWorker()
        self._connect_worker.connection_finished.connect(self._on_connection_finished)
        self._connect_worker.start()

    def _on_connection_finished(self, success: bool, message: str, state: ResolveState) -> None:
        """Handle background connection result on main thread."""
        self._is_resolve_connected = success
        self._resolve_state = state

        if success:
            app_logger.info(f"Resolve connected: {message}")
            db_manager.log_activity(
                level="INFO",
                category="RESOLVE_CONN",
                message=f"Connected to DaVinci Resolve ({state.project.name})"
            )
            self.connection_state_changed.emit(True)
            self.resolve_state_updated.emit(state)
            self.status_message_changed.emit(f"Connected to DaVinci Resolve - {state.project.name}")
            self.notification_emitted.emit("success", f"Connected to DaVinci Resolve! Project: '{state.project.name}'")
        else:
            app_logger.warning(f"Resolve connection failed: {message}")
            db_manager.log_activity(
                level="WARNING",
                category="RESOLVE_CONN",
                message=f"Connection failed: {message}"
            )
            self.connection_state_changed.emit(False)
            self.resolve_state_updated.emit(state)
            self.status_message_changed.emit("DaVinci Resolve Disconnected")
            self.notification_emitted.emit("warning", message)

    def _disconnect_resolve(self) -> None:
        """Disconnect Resolve service."""
        resolve_service.disconnect()
        self._is_resolve_connected = False
        self._resolve_state = ResolveState(is_connected=False)

        app_logger.info("DaVinci Resolve disconnected.")
        db_manager.log_activity(
            level="INFO",
            category="RESOLVE_CONN",
            message="Disconnected from DaVinci Resolve"
        )
        self.connection_state_changed.emit(False)
        self.resolve_state_updated.emit(self._resolve_state)
        self.status_message_changed.emit("DaVinci Resolve Disconnected")
        self.notification_emitted.emit("info", "Disconnected from DaVinci Resolve.")

    def _on_setting_changed(self, key: str, value: object) -> None:
        """Handle settings changes."""
        if key == "ai_provider":
            self._ai_provider = str(value)
            self.ai_provider_changed.emit(self._ai_provider)
            self.notification_emitted.emit("info", f"AI Provider changed to {self._ai_provider}")
