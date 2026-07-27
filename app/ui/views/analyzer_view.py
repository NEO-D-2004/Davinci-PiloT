"""
AI Vision & Audio Analyzer View Component for DaVinci PiloT.
Renders multi-agent speech transcripts, silence removal gaps, keyframe visual insights, and AI Smart Cut proposals.
Connects dynamically to active DaVinci Resolve Timeline and Media Pool clips.
"""

from typing import Optional, List, Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QProgressBar, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
from app.ai.multi_agent_pipeline import MultiAgentAnalyzer
from app.models.resolve_models import ResolveState
from app.models.analyzer_models import AnalysisReport, TranscriptSegment, SilenceGap, VisualFrameInsight, SmartCutProposal
from app.services.logger_service import app_logger


class AnalyzerWorkerThread(QThread):
    """Background worker thread for running multi-agent analysis on active Resolve clips."""
    analysis_completed = Signal(object)
    progress_updated = Signal(int, str)

    def __init__(self, asset_name: str, file_path: str, duration_sec: float) -> None:
        super().__init__()
        self.asset_name = asset_name
        self.file_path = file_path
        self.duration_sec = duration_sec
        self.pipeline = MultiAgentAnalyzer()

    def run(self) -> None:
        try:
            self.progress_updated.emit(20, f"Querying Nemotron ASR for '{self.asset_name}'...")
            self.msleep(200)

            self.progress_updated.emit(50, f"Sampling keyframes & querying MiniMax M3 Vision Agent...")
            self.msleep(200)

            self.progress_updated.emit(80, f"Synthesizing Smart Cuts via GLM-5.2 Master Agent...")
            report = self.pipeline.run_full_analysis(self.asset_name, self.file_path, self.duration_sec)

            self.progress_updated.emit(100, "Analysis Complete!")
            self.analysis_completed.emit(report)
        except Exception as e:
            app_logger.error(f"Error during AI analysis worker: {e}")


class AnalyzerView(QWidget):
    """Main AI Vision & Audio Analyzer View Component."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_report: Optional[AnalysisReport] = None
        self._worker: Optional[AnalyzerWorkerThread] = None
        self._clip_registry: Dict[str, Dict[str, Any]] = {}
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title
        header_layout = QHBoxLayout()
        title_lbl = QLabel("AI Vision & Audio Analyzer")
        title_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_lbl.setStyleSheet("color: #CDD6F4;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        self.summary_card = QLabel("Status: Select an active DaVinci Resolve clip to analyze")
        self.summary_card.setFont(QFont("Segoe UI", 10))
        self.summary_card.setStyleSheet("color: #A6ADC8; background-color: #181825; padding: 6px 14px; border-radius: 6px; border: 1px solid #313244;")
        header_layout.addWidget(self.summary_card)

        main_layout.addLayout(header_layout)

        # Control Panel & Action Bar
        control_card = QFrame()
        control_card.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        control_layout = QHBoxLayout(control_card)
        control_layout.setContentsMargins(14, 12, 14, 12)
        control_layout.setSpacing(14)

        asset_lbl = QLabel("Target Active Clip:")
        asset_lbl.setStyleSheet("color: #CDD6F4; font-weight: bold; font-size: 12px; border: none;")
        control_layout.addWidget(asset_lbl)

        self.asset_combo = QComboBox()
        self.asset_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 280px;
            }
        """)
        control_layout.addWidget(self.asset_combo, 1)

        self.run_btn = QPushButton("🚀 Run Multi-Agent Analysis")
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: #89B4FA;
                color: #11111B;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #B4BEFE;
            }
            QPushButton:disabled {
                background-color: #45475A;
                color: #6C7086;
            }
        """)
        self.run_btn.clicked.connect(self._start_analysis)
        control_layout.addWidget(self.run_btn)

        main_layout.addWidget(control_card)

        # Progress Indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                color: #CDD6F4;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #A6E3A1;
                border-radius: 5px;
            }
        """)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)

        # Tabbed View
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #313244;
                border-radius: 8px;
                background-color: #181825;
            }
            QTabBar::tab {
                background-color: #1E1E2E;
                color: #A6ADC8;
                padding: 8px 18px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #313244;
                color: #89B4FA;
                border-bottom: 2px solid #89B4FA;
            }
        """)

        # Tab 1: Speech Transcripts & Silence
        self.speech_tab = QWidget()
        speech_layout = QVBoxLayout(self.speech_tab)
        speech_layout.setContentsMargins(12, 12, 12, 12)

        self.transcript_table = QTableWidget()
        self.transcript_table.setColumnCount(5)
        self.transcript_table.setHorizontalHeaderLabels([
            "Timecode", "Speaker", "Transcript Text", "Confidence", "Type"
        ])
        self.transcript_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transcript_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.transcript_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E2E;
                color: #CDD6F4;
                gridline-color: #313244;
                border: 1px solid #313244;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #89B4FA;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #313244;
            }
        """)
        speech_layout.addWidget(self.transcript_table)
        self.tabs.addTab(self.speech_tab, "🗣️ Speech & Silence (Nemotron ASR)")

        # Tab 2: Vision Keyframes (MiniMax M3)
        self.vision_tab = QWidget()
        vision_layout = QVBoxLayout(self.vision_tab)
        vision_layout.setContentsMargins(12, 12, 12, 12)

        self.vision_table = QTableWidget()
        self.vision_table.setColumnCount(5)
        self.vision_table.setHorizontalHeaderLabels([
            "Frame #", "Timecode", "MiniMax M3 Scene Description", "Camera Motion", "Score"
        ])
        self.vision_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.vision_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.vision_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E2E;
                color: #CDD6F4;
                gridline-color: #313244;
                border: 1px solid #313244;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #F9E2AF;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #313244;
            }
        """)
        vision_layout.addWidget(self.vision_table)
        self.tabs.addTab(self.vision_tab, "👁️ Vision Keyframes (MiniMax M3)")

        # Tab 3: Smart Cut Proposals (GLM-5.2)
        self.cuts_tab = QWidget()
        cuts_layout = QVBoxLayout(self.cuts_tab)
        cuts_layout.setContentsMargins(12, 12, 12, 12)

        self.cuts_table = QTableWidget()
        self.cuts_table.setColumnCount(6)
        self.cuts_table.setHorizontalHeaderLabels([
            "Cut ID", "Start Timecode", "End Timecode", "Cut Type", "Reason", "Priority"
        ])
        self.cuts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cuts_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.cuts_table.setStyleSheet("""
            QTableWidget {
                background-color: #1E1E2E;
                color: #CDD6F4;
                gridline-color: #313244;
                border: 1px solid #313244;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #181825;
                color: #A6E3A1;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #313244;
            }
        """)
        cuts_layout.addWidget(self.cuts_table)
        self.tabs.addTab(self.cuts_tab, "✂️ Smart Cut Proposals (GLM-5.2)")

        main_layout.addWidget(self.tabs, 1)

    def update_resolve_state(self, state: ResolveState) -> None:
        """Populate target asset dropdown dynamically with actual clips from Resolve Timeline & Media Pool."""
        self.asset_combo.clear()
        self._clip_registry.clear()

        if not state or not state.is_connected:
            self.asset_combo.addItem("No DaVinci Resolve Connection")
            self.summary_card.setText("Status: Connect DaVinci Resolve to analyze active timeline clips")
            return

        # 1. Register Timeline Clips
        if state.timeline_structure:
            all_clips = state.timeline_structure.get_all_clips()
            for clip in all_clips:
                combo_title = f"[Timeline {clip.track_type.upper()}{clip.track_index}] {clip.name} ({clip.duration_frames}f)"
                duration_sec = clip.duration_frames / (state.timeline_structure.fps or 24.0)
                
                self._clip_registry[combo_title] = {
                    "name": clip.name,
                    "file_path": clip.source_path if clip.source_path != "N/A" else clip.name,
                    "duration_sec": max(duration_sec, 10.0),
                    "type": "timeline_clip"
                }
                self.asset_combo.addItem(combo_title)

        # 2. Register Media Pool Assets
        if state.media_pool_structure:
            mp_assets = state.media_pool_structure.get_all_assets()
            for asset in mp_assets:
                combo_title = f"[Media Bin] {asset.name} ({asset.resolution})"
                if combo_title not in self._clip_registry:
                    self._clip_registry[combo_title] = {
                        "name": asset.name,
                        "file_path": asset.file_path,
                        "duration_sec": 45.0,
                        "type": "media_asset"
                    }
                    self.asset_combo.addItem(combo_title)

        if self.asset_combo.count() == 0:
            self.asset_combo.addItem(f"Active Project: '{state.project.name}' Timeline Clips")
            self._clip_registry[f"Active Project: '{state.project.name}' Timeline Clips"] = {
                "name": state.timeline.name or "Timeline",
                "file_path": state.project.name,
                "duration_sec": 45.0,
                "type": "project"
            }

        self.summary_card.setText(f"Connected: {self.asset_combo.count()} active Resolve clips ready for AI Analysis")

    def _start_analysis(self) -> None:
        selected_text = self.asset_combo.currentText()
        if not selected_text or selected_text == "No DaVinci Resolve Connection":
            QMessageBox.warning(self, "No Clip Selected", "Please select a valid clip from your DaVinci Resolve Timeline!")
            return

        clip_data = self._clip_registry.get(selected_text, {
            "name": selected_text,
            "file_path": selected_text,
            "duration_sec": 45.0
        })

        self.run_btn.setEnabled(False)
        self.progress_bar.setValue(10)
        self.progress_bar.setFormat(f"Connecting to NVIDIA NIM for '{clip_data['name']}'...")
        self.progress_bar.show()

        self._worker = AnalyzerWorkerThread(
            asset_name=clip_data["name"],
            file_path=clip_data["file_path"],
            duration_sec=clip_data["duration_sec"]
        )
        self._worker.progress_updated.connect(self._on_progress_updated)
        self._worker.analysis_completed.connect(self.display_report)
        self._worker.start()

    def _on_progress_updated(self, val: int, msg: str) -> None:
        self.progress_bar.setValue(val)
        self.progress_bar.setFormat(f"{msg} ({val}%)")

    def display_report(self, report: AnalysisReport) -> None:
        self._current_report = report
        self.run_btn.setEnabled(True)
        self.progress_bar.hide()

        # Update Summary Banner
        self.summary_card.setText(
            f"Analyzed Clip: '{report.asset_name}' | {len(report.segments)} Speech Segments | "
            f"✂️ {len(report.cut_proposals)} Smart Cuts Proposed (Saved {report.total_silence_time:.1f}s Silence)"
        )

        # 1. Render Transcripts Table
        self.transcript_table.setRowCount(len(report.segments))
        for row, seg in enumerate(report.segments):
            type_text = "Filler Word" if seg.is_filler else "Speech"
            self.transcript_table.setItem(row, 0, QTableWidgetItem(seg.start_timecode))
            self.transcript_table.setItem(row, 1, QTableWidgetItem(seg.speaker))
            self.transcript_table.setItem(row, 2, QTableWidgetItem(seg.text))
            self.transcript_table.setItem(row, 3, QTableWidgetItem(f"{int(seg.confidence * 100)}%"))
            self.transcript_table.setItem(row, 4, QTableWidgetItem(type_text))

        # 2. Render Vision Keyframes Table
        self.vision_table.setRowCount(len(report.frame_insights))
        for row, fi in enumerate(report.frame_insights):
            self.vision_table.setItem(row, 0, QTableWidgetItem(str(fi.frame_idx)))
            self.vision_table.setItem(row, 1, QTableWidgetItem(fi.timecode))
            self.vision_table.setItem(row, 2, QTableWidgetItem(fi.scene_description))
            self.vision_table.setItem(row, 3, QTableWidgetItem(fi.camera_movement))
            self.vision_table.setItem(row, 4, QTableWidgetItem(f"{fi.quality_score} / 10"))

        # 3. Render Smart Cut Proposals Table
        self.cuts_table.setRowCount(len(report.cut_proposals))
        for row, cut in enumerate(report.cut_proposals):
            self.cuts_table.setItem(row, 0, QTableWidgetItem(cut.cut_id))
            self.cuts_table.setItem(row, 1, QTableWidgetItem(cut.start_timecode))
            self.cuts_table.setItem(row, 2, QTableWidgetItem(cut.end_timecode))
            self.cuts_table.setItem(row, 3, QTableWidgetItem(cut.cut_type))
            self.cuts_table.setItem(row, 4, QTableWidgetItem(cut.reason))
            self.cuts_table.setItem(row, 5, QTableWidgetItem(cut.priority))
