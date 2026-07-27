"""
Dashboard View component for DaVinci PiloT.
Renders central dashboard workspace with system status, metrics cards, and live activity log console.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QGroupBox, QTextEdit, QPushButton, QFrame, QSplitter
)
from app.services.logger_service import logger_service
from app.models.resolve_models import ResolveState


class MetricCard(QFrame):
    """Card widget displaying key metrics."""

    def __init__(self, title: str, value: str, subtitle: str, color: str = "#89B4FA", parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #181825;
                border: 1px solid #313244;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        t_label = QLabel(title, self)
        t_label.setStyleSheet("color: #A6ADC8; font-size: 11px; font-weight: bold;")

        v_label = QLabel(value, self)
        v_label.setStyleSheet("color: #CDD6F4; font-size: 18px; font-weight: bold;")
        self.val_label = v_label

        s_label = QLabel(subtitle, self)
        s_label.setStyleSheet("color: #6C7086; font-size: 10px;")
        self.sub_label = s_label

        layout.addWidget(t_label)
        layout.addWidget(v_label)
        layout.addWidget(s_label)

    def set_value(self, value: str, subtitle: str = "") -> None:
        self.val_label.setText(value)
        if subtitle:
            self.sub_label.setText(subtitle)


class DashboardView(QWidget):
    """Main Application Dashboard View."""

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self._init_ui()
        # Connect log signals to UI log output
        logger_service.signal_emitter.log_emitted.connect(self.append_log)

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Header Title
        header = QLabel("DaVinci PiloT Command Center", self)
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #89B4FA;")
        main_layout.addWidget(header)

        # Metrics Row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self.card_resolve = MetricCard(
            "DAVINCI RESOLVE", "Disconnected", "Status: Inactive", "#F38BA8", self
        )
        self.card_project = MetricCard(
            "CURRENT PROJECT", "None", "No project loaded", "#FAB387", self
        )
        self.card_timeline = MetricCard(
            "ACTIVE TIMELINE", "0 Clips", "0 Tracks", "#89B4FA", self
        )
        self.card_ai = MetricCard(
            "AI PROVIDER", "NVIDIA NIM", "GLM-5.2 + Multi-Agent", "#A6E3A1", self
        )

        metrics_layout.addWidget(self.card_resolve)
        metrics_layout.addWidget(self.card_project)
        metrics_layout.addWidget(self.card_timeline)
        metrics_layout.addWidget(self.card_ai)

        main_layout.addLayout(metrics_layout)

        # Splitter between status panels & log output console
        splitter = QSplitter(Qt.Orientation.Vertical, self)

        # Overview Box
        overview_group = QGroupBox("System & DaVinci Resolve Integration Status", self)
        overview_layout = QVBoxLayout(overview_group)

        self.info_text = QLabel(
            "• Milestone 2 (DaVinci Resolve Connection) Active.\n"
            "• Application communicates directly with DaVinci Resolve via official fusionscript.dll Scripting API.\n"
            "• Next Milestone (Milestone 3): Timeline Explorer (Tracks, Clips, Markers, Transitions, Metadata).",
            self
        )
        self.info_text.setStyleSheet("color: #CDD6F4; line-height: 1.4;")
        overview_layout.addWidget(self.info_text)

        splitter.addWidget(overview_group)

        # Console Log Panel
        log_group = QGroupBox("Live Activity Log Console", self)
        log_layout = QVBoxLayout(log_group)

        self.log_console = QTextEdit(self)
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Consolas", 10))
        self.log_console.setStyleSheet("""
            QTextEdit {
                background-color: #11111B;
                color: #A6ADC8;
                border: 1px solid #313244;
                border-radius: 6px;
            }
        """)
        log_layout.addWidget(self.log_console)

        splitter.addWidget(log_group)
        splitter.setSizes([140, 260])

        main_layout.addWidget(splitter)

    def append_log(self, level: str, message: str) -> None:
        """Append log line with colored formatting."""
        color_map = {
            "DEBUG": "#9399B2",
            "INFO": "#89B4FA",
            "WARNING": "#F9E2AF",
            "ERROR": "#F38BA8",
            "CRITICAL": "#F38BA8",
        }
        color = color_map.get(level, "#CDD6F4")
        html_msg = f'<span style="color: {color};"><b>[{level}]</b> {message}</span>'
        self.log_console.append(html_msg)

    def update_connection_state(self, connected: bool) -> None:
        if connected:
            self.card_resolve.set_value("Connected", "Resolve Scripting Active")
        else:
            self.card_resolve.set_value("Disconnected", "Status: Inactive")
            self.card_project.set_value("None", "No project loaded")
            self.card_timeline.set_value("0 Clips", "0 Tracks")

    def update_resolve_state(self, state: ResolveState) -> None:
        """Update metrics cards with live ResolveState data."""
        if state.is_connected:
            self.card_resolve.set_value(f"v{state.resolve_version}", state.product_name)
            
            p_name = state.project.name
            p_sub = f"{state.project.resolution} @ {state.project.frame_rate}" if state.project.is_loaded else "No project open"
            self.card_project.set_value(p_name, p_sub)

            t_name = state.timeline.name if state.timeline.is_active else "No Timeline"
            t_sub = f"{state.timeline.total_clips} Clips ({state.timeline.video_tracks_count}V / {state.timeline.audio_tracks_count}A)"
            self.card_timeline.set_value(t_name, t_sub)
        else:
            self.update_connection_state(False)
