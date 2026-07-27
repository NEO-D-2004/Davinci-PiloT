"""
Menu Bar component for DaVinci PiloT.
Provides File, Edit, View, Resolve, AI, Tools, and Help menus with keyboard shortcuts and signals.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar, QWidget


class MenuBarSignals(QObject):
    open_settings = Signal()
    exit_app = Signal()
    connect_resolve = Signal()
    disconnect_resolve = Signal()
    open_ai_chat = Signal()
    show_about = Signal()
    toggle_log_panel = Signal()


class AppMenuBar(QMenuBar):
    """Main Application Menu Bar."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.signals = MenuBarSignals()
        self._create_menus()

    def _create_menus(self) -> None:
        # File Menu
        file_menu = self.addMenu("&File")

        settings_act = QAction("&Settings", self)
        settings_act.setShortcut(QKeySequence("Ctrl+,"))
        settings_act.triggered.connect(self.signals.open_settings.emit)
        file_menu.addAction(settings_act)

        file_menu.addSeparator()

        exit_act = QAction("E&xit", self)
        exit_act.setShortcut(QKeySequence("Ctrl+Q"))
        exit_act.triggered.connect(self.signals.exit_app.emit)
        file_menu.addAction(exit_act)

        # Edit Menu
        edit_menu = self.addMenu("&Edit")
        undo_act = QAction("&Undo", self)
        undo_act.setShortcut(QKeySequence.Undo)
        edit_menu.addAction(undo_act)
        redo_act = QAction("&Redo", self)
        redo_act.setShortcut(QKeySequence.Redo)
        edit_menu.addAction(redo_act)

        # View Menu
        view_menu = self.addMenu("&View")
        toggle_logs_act = QAction("Toggle &Log Panel", self)
        toggle_logs_act.setShortcut(QKeySequence("Ctrl+L"))
        toggle_logs_act.triggered.connect(self.signals.toggle_log_panel.emit)
        view_menu.addAction(toggle_logs_act)

        # DaVinci Resolve Menu
        resolve_menu = self.addMenu("&Resolve")
        connect_act = QAction("&Connect to Resolve", self)
        connect_act.setShortcut(QKeySequence("Ctrl+Shift+C"))
        connect_act.triggered.connect(self.signals.connect_resolve.emit)
        resolve_menu.addAction(connect_act)

        disconnect_act = QAction("&Disconnect", self)
        disconnect_act.triggered.connect(self.signals.disconnect_resolve.emit)
        resolve_menu.addAction(disconnect_act)

        # AI Menu
        ai_menu = self.addMenu("&AI")
        ai_chat_act = QAction("Open AI Assistant &Chat", self)
        ai_chat_act.setShortcut(QKeySequence("Ctrl+Shift+A"))
        ai_chat_act.triggered.connect(self.signals.open_ai_chat.emit)
        ai_menu.addAction(ai_chat_act)

        # Tools Menu
        tools_menu = self.addMenu("&Tools")

        # Help Menu
        help_menu = self.addMenu("&Help")
        about_act = QAction("&About DaVinci PiloT", self)
        about_act.triggered.connect(self.signals.show_about.emit)
        help_menu.addAction(about_act)
