"""
Timeline Explorer View for DaVinci PiloT.
Provides an interactive visual track diagram, detailed clip table, marker list, and real-time clip filtering.
"""

from typing import Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget, QScrollArea,
    QFrame, QPushButton, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from app.models.timeline_models import TimelineStructure, TrackInfo, ClipItem, TimelineMarker


class TrackLaneWidget(QFrame):
    """Visual track lane rendering clip blocks horizontally."""

    def __init__(self, track: TrackInfo, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.track = track
        self._init_ui()

    def _init_ui(self) -> None:
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #1E1E2E;
                border: 1px solid #313244;
                border-radius: 6px;
                margin-bottom: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)

        # Track Header Label
        track_prefix = "V" if self.track.track_type == "video" else "A"
        header_color = "#89B4FA" if self.track.track_type == "video" else "#A6E3A1"

        track_label = QLabel(f"[{track_prefix}{self.track.track_index}] {self.track.name}")
        track_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        track_label.setStyleSheet(f"color: {header_color}; min-width: 120px;")
        layout.addWidget(track_label)

        # Clip blocks scroll container
        clips_area = QWidget()
        clips_layout = QHBoxLayout(clips_area)
        clips_layout.setContentsMargins(0, 0, 0, 0)
        clips_layout.setSpacing(6)
        clips_layout.setAlignment(Qt.AlignLeft)

        if not self.track.clips:
            empty_lbl = QLabel("No clips on track")
            empty_lbl.setStyleSheet("color: #6C7086; font-style: italic; font-size: 11px;")
            clips_layout.addWidget(empty_lbl)
        else:
            for clip in self.track.clips:
                clip_btn = QPushButton(f"  {clip.name}  ")
                clip_btn.setToolTip(
                    f"Clip: {clip.name}\n"
                    f"Track: {clip.track_type.upper()} {clip.track_index}\n"
                    f"Start: {clip.start_timecode} | Duration: {clip.duration_frames} frames\n"
                    f"Source: {clip.source_path}"
                )
                
                # Dynamic clip block styling
                bg_color = "#313244"
                if clip.track_type == "video":
                    bg_color = "#2E3C56"
                else:
                    bg_color = "#2D4438"

                clip_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg_color};
                        color: #CDD6F4;
                        border: 1px solid #45475A;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-size: 11px;
                        font-weight: 500;
                    }}
                    QPushButton:hover {{
                        background-color: #45475A;
                        border-color: #89B4FA;
                        color: #FFFFFF;
                    }}
                """)
                clips_layout.addWidget(clip_btn)

        layout.addWidget(clips_area, 1)


class TimelineView(QWidget):
    """Main Timeline Explorer View Component."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_structure: Optional[TimelineStructure] = None
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title & Summary
        header_layout = QHBoxLayout()
        title_lbl = QLabel("Timeline Explorer")
        title_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_lbl.setStyleSheet("color: #CDD6F4;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        self.summary_lbl = QLabel("Timeline: None | 0 Clips (0V / 0A)")
        self.summary_lbl.setFont(QFont("Segoe UI", 10))
        self.summary_lbl.setStyleSheet("color: #A6ADC8; background-color: #181825; padding: 6px 14px; border-radius: 6px; border: 1px solid #313244;")
        header_layout.addWidget(self.summary_lbl)

        main_layout.addLayout(header_layout)

        # Search & Filter Controls Bar
        filter_card = QFrame()
        filter_card.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(12)

        # Search input
        search_icon_lbl = QLabel("🔍")
        search_icon_lbl.setStyleSheet("border: none; font-size: 14px;")
        filter_layout.addWidget(search_icon_lbl)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search clip name, source file path, or keyword...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid #89B4FA;
            }
        """)
        self.search_edit.textChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.search_edit, 1)

        # Filter by Track Type
        self.track_filter = QComboBox()
        self.track_filter.addItems(["All Tracks", "Video Tracks Only", "Audio Tracks Only"])
        self.track_filter.setStyleSheet("""
            QComboBox {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                min-width: 140px;
            }
        """)
        self.track_filter.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.track_filter)

        main_layout.addWidget(filter_card)

        # Tabbed View: Visual Track Graph vs Master Clip Table vs Markers
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

        # Tab 1: Visual Track Graph
        self.track_graph_tab = QWidget()
        graph_layout = QVBoxLayout(self.track_graph_tab)
        graph_layout.setContentsMargins(12, 12, 12, 12)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.track_graph_container = QWidget()
        self.track_graph_layout = QVBoxLayout(self.track_graph_container)
        self.track_graph_layout.setContentsMargins(0, 0, 0, 0)
        self.track_graph_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.track_graph_container)
        graph_layout.addWidget(self.scroll_area)

        self.tabs.addTab(self.track_graph_tab, "📊 Visual Track Lanes")

        # Tab 2: Clips Master Table
        self.clips_table_tab = QWidget()
        table_layout = QVBoxLayout(self.clips_table_tab)
        table_layout.setContentsMargins(12, 12, 12, 12)

        self.clips_table = QTableWidget()
        self.clips_table.setColumnCount(7)
        self.clips_table.setHorizontalHeaderLabels([
            "Clip Name", "Track", "Start Frame", "End Frame", "Duration", "Source File Path", "Flag"
        ])
        self.clips_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.clips_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.clips_table.setStyleSheet("""
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
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #45475A;
                color: #FFFFFF;
            }
        """)
        table_layout.addWidget(self.clips_table)

        self.tabs.addTab(self.clips_table_tab, "📋 Clip Master Table")

        # Tab 3: Timeline Markers
        self.markers_tab = QWidget()
        markers_layout = QVBoxLayout(self.markers_tab)
        markers_layout.setContentsMargins(12, 12, 12, 12)

        self.markers_table = QTableWidget()
        self.markers_table.setColumnCount(5)
        self.markers_table.setHorizontalHeaderLabels([
            "Frame", "Timecode", "Color", "Marker Name", "Notes"
        ])
        self.markers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.markers_table.setStyleSheet("""
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
        markers_layout.addWidget(self.markers_table)

        self.tabs.addTab(self.markers_tab, "📌 Markers & Notes")

        main_layout.addWidget(self.tabs, 1)

    def update_timeline_structure(self, structure: Optional[TimelineStructure]) -> None:
        """Update view with new TimelineStructure payload."""
        self._current_structure = structure

        if not structure or structure.name == "None":
            self.summary_lbl.setText("Timeline: None | 0 Clips (0V / 0A)")
            self._clear_views()
            return

        # Update Summary Bar
        self.summary_lbl.setText(
            f"Timeline: '{structure.name}' | {structure.total_clips} Clips "
            f"({structure.total_video_clips}V / {structure.total_audio_clips}A) @ {structure.fps} fps"
        )

        self._render_structure(structure)

    def _clear_views(self) -> None:
        # Clear Track Lanes
        while self.track_graph_layout.count():
            item = self.track_graph_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear Tables
        self.clips_table.setRowCount(0)
        self.markers_table.setRowCount(0)

    def _render_structure(self, structure: TimelineStructure) -> None:
        self._clear_views()

        # 1. Render Track Lanes
        all_tracks = structure.video_tracks + structure.audio_tracks
        for track in all_tracks:
            lane = TrackLaneWidget(track)
            self.track_graph_layout.addWidget(lane)

        # 2. Render Clips Table
        all_clips = structure.get_all_clips()
        self.clips_table.setRowCount(len(all_clips))

        for row, clip in enumerate(all_clips):
            self.clips_table.setItem(row, 0, QTableWidgetItem(clip.name))
            self.clips_table.setItem(row, 1, QTableWidgetItem(f"{clip.track_type.upper()} {clip.track_index}"))
            self.clips_table.setItem(row, 2, QTableWidgetItem(str(clip.start_frame)))
            self.clips_table.setItem(row, 3, QTableWidgetItem(str(clip.end_frame)))
            self.clips_table.setItem(row, 4, QTableWidgetItem(f"{clip.duration_frames} f"))
            self.clips_table.setItem(row, 5, QTableWidgetItem(clip.source_path))
            self.clips_table.setItem(row, 6, QTableWidgetItem(clip.flag_color))

        # 3. Render Markers Table
        self.markers_table.setRowCount(len(structure.markers))
        for row, marker in enumerate(structure.markers):
            self.markers_table.setItem(row, 0, QTableWidgetItem(str(marker.frame)))
            self.markers_table.setItem(row, 1, QTableWidgetItem(marker.timecode))
            self.markers_table.setItem(row, 2, QTableWidgetItem(marker.color))
            self.markers_table.setItem(row, 3, QTableWidgetItem(marker.name or "Marker"))
            self.markers_table.setItem(row, 4, QTableWidgetItem(marker.note or "-"))

    def _apply_filters(self) -> None:
        """Filter clips in master table based on search query and track filter."""
        query = self.search_edit.text().strip().lower()
        track_mode = self.track_filter.currentText()

        if not self._current_structure:
            return

        all_clips = self._current_structure.get_all_clips()
        filtered_rows = 0

        self.clips_table.setRowCount(0)

        for clip in all_clips:
            # Filter track mode
            if track_mode == "Video Tracks Only" and clip.track_type != "video":
                continue
            if track_mode == "Audio Tracks Only" and clip.track_type != "audio":
                continue

            # Search query matching
            if query:
                match = (
                    query in clip.name.lower() or
                    query in clip.source_path.lower() or
                    query in clip.flag_color.lower()
                )
                if not match:
                    continue

            # Add matching clip row
            row = self.clips_table.rowCount()
            self.clips_table.insertRow(row)
            self.clips_table.setItem(row, 0, QTableWidgetItem(clip.name))
            self.clips_table.setItem(row, 1, QTableWidgetItem(f"{clip.track_type.upper()} {clip.track_index}"))
            self.clips_table.setItem(row, 2, QTableWidgetItem(str(clip.start_frame)))
            self.clips_table.setItem(row, 3, QTableWidgetItem(str(clip.end_frame)))
            self.clips_table.setItem(row, 4, QTableWidgetItem(f"{clip.duration_frames} f"))
            self.clips_table.setItem(row, 5, QTableWidgetItem(clip.source_path))
            self.clips_table.setItem(row, 6, QTableWidgetItem(clip.flag_color))
