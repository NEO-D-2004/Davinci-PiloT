"""
Main Window for DaVinci PiloT.
Assembles MenuBar, ToolBar, StatusBar, DashboardView, and NotificationCenter.
"""

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QMessageBox, QWidget, QVBoxLayout
from app.ui.components import AppMenuBar, AppToolBar, AppStatusBar, NotificationCenter, NotificationType
from app.ui.views import DashboardView, SettingsDialog
from app.viewmodels import MainViewModel
from app.services.logger_service import app_logger


class MainWindow(QMainWindow):
    """Main Application Window."""

    def __init__(self, viewModel: MainViewModel) -> None:
        super().__init__()
        self.viewModel = viewModel
        self.setWindowTitle("DaVinci PiloT - AI Copilot for DaVinci Resolve")
        self.resize(1280, 800)
        self.setMinimumSize(960, 600)
        
        self.notification_center = NotificationCenter(self)
        self._init_ui()
        self._load_stylesheet()
        self._bind_viewmodel()

    def _init_ui(self) -> None:
        # Menu Bar
        self.app_menu_bar = AppMenuBar(self)
        self.setMenuBar(self.app_menu_bar)

        # Toolbar
        self.app_toolbar = AppToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.app_toolbar)

        # Status Bar
        self.app_status_bar = AppStatusBar(self)
        self.setStatusBar(self.app_status_bar)

        # Central View
        self.dashboard_view = DashboardView(self)
        self.setCentralWidget(self.dashboard_view)

    def _load_stylesheet(self) -> None:
        """Load QSS dark theme stylesheet."""
        qss_path = Path(__file__).resolve().parent.parent / "assets" / "styles" / "dark_theme.qss"
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
            app_logger.info("Loaded Dark Theme QSS stylesheet.")

    def _bind_viewmodel(self) -> None:
        """Bind UI events and ViewModel signals."""
        # Menu Bar Signals
        self.app_menu_bar.signals.open_settings.connect(self.open_settings_dialog)
        self.app_menu_bar.signals.exit_app.connect(self.close)
        self.app_menu_bar.signals.connect_resolve.connect(self.viewModel.toggle_resolve_connection)
        self.app_menu_bar.signals.disconnect_resolve.connect(self.viewModel.toggle_resolve_connection)
        self.app_menu_bar.signals.open_ai_chat.connect(self.open_ai_chat)
        self.app_menu_bar.signals.show_about.connect(self.show_about_dialog)

        # Toolbar Signals
        self.app_toolbar.signals.connect_resolve.connect(self.viewModel.toggle_resolve_connection)
        self.app_toolbar.signals.open_settings.connect(self.open_settings_dialog)
        self.app_toolbar.signals.open_ai_chat.connect(self.open_ai_chat)

        # ViewModel State Signals
        self.viewModel.connection_state_changed.connect(self.on_connection_state_changed)
        self.viewModel.resolve_state_updated.connect(self.dashboard_view.update_resolve_state)
        self.viewModel.status_message_changed.connect(self.app_status_bar.show_message)
        self.viewModel.notification_emitted.connect(self.handle_notification_signal)
        self.viewModel.ai_provider_changed.connect(self.app_status_bar.set_ai_provider)

        # Initial ViewModel sync
        self.app_status_bar.set_ai_provider(self.viewModel.ai_provider)

    def on_connection_state_changed(self, connected: bool) -> None:
        """Sync UI widgets when Resolve connection state changes."""
        self.app_toolbar.update_connection_status(connected)
        self.dashboard_view.update_connection_state(connected)

    def handle_notification_signal(self, n_type_str: str, message: str) -> None:
        """Show toast notification based on signal."""
        type_map = {
            "info": NotificationType.INFO,
            "success": NotificationType.SUCCESS,
            "warning": NotificationType.WARNING,
            "error": NotificationType.ERROR,
        }
        n_type = type_map.get(n_type_str.lower(), NotificationType.INFO)
        self.notification_center.notify(message, n_type)

    def open_settings_dialog(self) -> None:
        """Open settings dialog window."""
        dialog = SettingsDialog(self)
        dialog.exec()

    def open_ai_chat(self) -> None:
        """Quick trigger for AI Chat (Milestone 6)."""
        self.notification_center.info("AI Chat Panel will be fully integrated in Milestone 6.")

    def show_about_dialog(self) -> None:
        """Display About dialog."""
        QMessageBox.about(
            self,
            "About DaVinci PiloT",
            "<h3>DaVinci PiloT v0.1.0</h3>"
            "<p>An AI-powered desktop copilot that automates editing inside DaVinci Resolve "
            "using the official Resolve Scripting API.</p>"
            "<p><b>Architecture:</b> PySide6 (Qt) + Python 3.13+ + MVVM</p>"
        )
