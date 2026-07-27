"""
Splash Screen component for DaVinci PiloT initialization.
Displays branded splash widget with loading status text and animated progress bar.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter, QLinearGradient
from PySide6.QtWidgets import QSplashScreen, QVBoxLayout, QLabel, QProgressBar, QWidget, QGraphicsDropShadowEffect
from app.config import config


class SplashScreen(QSplashScreen):
    """Custom animated Splash Screen widget."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(520, 320)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        # Main Card Widget
        container = QWidget(self)
        container.setObjectName("SplashCard")
        container.setStyleSheet("""
            QWidget#SplashCard {
                background-color: #181825;
                border: 1px solid #45475A;
                border-radius: 12px;
            }
        """)

        # Drop Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(container)
        card_layout.setContentsMargins(30, 30, 30, 30)

        # Title Label
        title_label = QLabel("DaVinci PiloT", container)
        title_font = QFont("Segoe UI", 26, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #89B4FA; background: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Subtitle Label
        sub_label = QLabel("AI Copilot for DaVinci Resolve", container)
        sub_font = QFont("Segoe UI", 12)
        sub_label.setFont(sub_font)
        sub_label.setStyleSheet("color: #A6ADC8; background: transparent;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Loading Message
        self.status_label = QLabel("Initializing application components...", container)
        status_font = QFont("Segoe UI", 10)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #BAC2DE; background: transparent;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Progress Bar
        self.progress_bar = QProgressBar(container)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(10)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #11111B;
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #89B4FA, stop:1 #74C7EC);
                border-radius: 4px;
            }
        """)

        # Version label
        ver_label = QLabel("v0.1.0 (Milestone 1)", container)
        ver_label.setFont(QFont("Segoe UI", 8))
        ver_label.setStyleSheet("color: #6C7086; background: transparent;")
        ver_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title_label)
        card_layout.addWidget(sub_label)
        card_layout.addStretch()
        card_layout.addWidget(self.status_label)
        card_layout.addWidget(self.progress_bar)
        card_layout.addSpacing(10)
        card_layout.addWidget(ver_label)

        layout.addWidget(container)

    def set_progress(self, value: int, message: str) -> None:
        """Update splash screen progress and status message."""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.repaint()
