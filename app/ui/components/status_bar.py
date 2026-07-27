"""
Status Bar component for DaVinci PiloT.
Displays current action status message, progress bar for asynchronous tasks, and connection status.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStatusBar, QLabel, QProgressBar, QWidget


class AppStatusBar(QStatusBar):
    """Main Application Status Bar."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        # Message label
        self.message_label = QLabel("Ready", self)
        self.message_label.setStyleSheet("color: #CDD6F4; padding: 2px 8px;")
        self.addWidget(self.message_label, stretch=1)

        # Task Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFixedSize(140, 14)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.addPermanentWidget(self.progress_bar)

        # AI Provider Badge
        self.ai_badge = QLabel("AI: Gemini", self)
        self.ai_badge.setStyleSheet("""
            QLabel {
                color: #89B4FA;
                background-color: #252538;
                padding: 2px 8px;
                border-radius: 4px;
                border: 1px solid #45475A;
            }
        """)
        self.addPermanentWidget(self.ai_badge)

    def show_message(self, message: str, timeout: int = 5000) -> None:
        """Display status message."""
        self.message_label.setText(message)
        if timeout > 0:
            super().showMessage(message, timeout)

    def start_progress(self, max_value: int = 100) -> None:
        """Show progress bar and start animation."""
        self.progress_bar.setRange(0, max_value)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)

    def update_progress(self, value: int) -> None:
        """Update progress bar value."""
        self.progress_bar.setValue(value)

    def stop_progress(self) -> None:
        """Hide progress bar."""
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

    def set_ai_provider(self, provider_name: str) -> None:
        """Update AI provider badge."""
        self.ai_badge.setText(f"AI: {provider_name.capitalize()}")
