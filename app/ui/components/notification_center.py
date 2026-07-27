"""
Toast Notification Center component for DaVinci PiloT.
Renders floating animated notifications over the main application view.
"""

from enum import Enum
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QGraphicsDropShadowEffect


class NotificationType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


NOTIFICATION_COLORS = {
    NotificationType.INFO: ("#89B4FA", "#1E1E2E", "ℹ️"),
    NotificationType.SUCCESS: ("#A6E3A1", "#1E1E2E", "✅"),
    NotificationType.WARNING: ("#F9E2AF", "#11111B", "⚠️"),
    NotificationType.ERROR: ("#F38BA8", "#1E1E2E", "❌"),
}


class NotificationToast(QWidget):
    """Floating Notification Toast Widget."""

    def __init__(self, parent: QWidget, message: str, n_type: NotificationType = NotificationType.INFO, duration_ms: int = 4000) -> None:
        super().__init__(parent)
        self.message = message
        self.n_type = n_type
        self.duration_ms = duration_ms
        self._init_ui()

    def _init_ui(self) -> None:
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.SubWindow)

        border_color, bg_color, icon = NOTIFICATION_COLORS[self.n_type]

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        content = QWidget(self)
        content.setObjectName("ToastContent")
        content.setStyleSheet(f"""
            QWidget#ToastContent {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-left: 5px solid {border_color};
                border-radius: 8px;
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        content.setGraphicsEffect(shadow)

        c_layout = QHBoxLayout(content)
        c_layout.setContentsMargins(12, 8, 12, 8)

        icon_label = QLabel(icon, content)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))

        msg_label = QLabel(self.message, content)
        msg_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        msg_label.setStyleSheet("color: #CDD6F4;")

        c_layout.addWidget(icon_label)
        c_layout.addWidget(msg_label)

        layout.addWidget(content)

        # Opacity animation for fade in/out
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(250)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out.finished.connect(self.close)

        QTimer.singleShot(self.duration_ms, self.start_fade_out)

    def show_toast(self) -> None:
        self.show()
        self.fade_in.start()

    def start_fade_out(self) -> None:
        self.fade_out.start()


class NotificationCenter:
    """Manages spawning toast notifications over parent window."""

    def __init__(self, parent_window: QWidget) -> None:
        self.parent_window = parent_window

    def notify(self, message: str, n_type: NotificationType = NotificationType.INFO, duration_ms: int = 4000) -> None:
        toast = NotificationToast(self.parent_window, message, n_type, duration_ms)
        # Position toast near top-right of parent window
        parent_rect = self.parent_window.rect()
        toast.adjustSize()
        toast_width = toast.width()
        toast.move(parent_rect.right() - toast_width - 30, parent_rect.top() + 60)
        toast.show_toast()

    def info(self, message: str) -> None:
        self.notify(message, NotificationType.INFO)

    def success(self, message: str) -> None:
        self.notify(message, NotificationType.SUCCESS)

    def warning(self, message: str) -> None:
        self.notify(message, NotificationType.WARNING)

    def error(self, message: str) -> None:
        self.notify(message, NotificationType.ERROR)
