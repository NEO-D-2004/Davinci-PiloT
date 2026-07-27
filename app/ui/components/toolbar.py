"""
Action Toolbar component for DaVinci PiloT.
Provides quick-access action buttons and indicators.
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QToolBar, QWidget, QPushButton, QLabel, QHBoxLayout, QFrame


class ToolBarSignals(QObject):
    connect_resolve = Signal()
    open_settings = Signal()
    open_ai_chat = Signal()


class AppToolBar(QToolBar):
    """Main Application Action Toolbar."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__("Main Toolbar", parent)
        self.signals = ToolBarSignals()
        self.setMovable(False)
        self._init_ui()

    def _init_ui(self) -> None:
        # Resolve Connection Quick Button
        self.btn_resolve = QPushButton("🔗 Connect Resolve", self)
        self.btn_resolve.setToolTip("Attempt connection to local DaVinci Resolve instance")
        self.btn_resolve.clicked.connect(self.signals.connect_resolve.emit)
        self.addWidget(self.btn_resolve)

        self.addSeparator()

        # AI Assistant Quick Button
        self.btn_ai = QPushButton("🤖 AI Assistant", self)
        self.btn_ai.setToolTip("Open AI Copilot Chat panel")
        self.btn_ai.clicked.connect(self.signals.open_ai_chat.emit)
        self.addWidget(self.btn_ai)

        self.addSeparator()

        # Settings Quick Button
        self.btn_settings = QPushButton("⚙️ Settings", self)
        self.btn_settings.setToolTip("Configure application preferences and AI keys")
        self.btn_settings.clicked.connect(self.signals.open_settings.emit)
        self.addWidget(self.btn_settings)

        # Flexible Spacer
        spacer = QWidget(self)
        spacer.setSizePolicy(
            self.sizePolicy().Policy.Expanding,
            self.sizePolicy().Policy.Preferred
        )
        self.addWidget(spacer)

        # Status badge indicator
        self.status_badge = QLabel("● Resolve Disconnected", self)
        self.status_badge.setStyleSheet("""
            QLabel {
                color: #F38BA8;
                font-weight: bold;
                padding: 4px 10px;
                background-color: #313244;
                border-radius: 6px;
            }
        """)
        self.addWidget(self.status_badge)

    def update_connection_status(self, connected: bool) -> None:
        """Update connection indicator badge."""
        if connected:
            self.status_badge.setText("● Resolve Connected")
            self.status_badge.setStyleSheet("""
                QLabel {
                    color: #A6E3A1;
                    font-weight: bold;
                    padding: 4px 10px;
                    background-color: #313244;
                    border-radius: 6px;
                }
            """)
            self.btn_resolve.setText("Disconnect Resolve")
        else:
            self.status_badge.setText("● Resolve Disconnected")
            self.status_badge.setStyleSheet("""
                QLabel {
                    color: #F38BA8;
                    font-weight: bold;
                    padding: 4px 10px;
                    background-color: #313244;
                    border-radius: 6px;
                }
            """)
            self.btn_resolve.setText("🔗 Connect Resolve")
