"""
Media Pool & Asset Manager View Component for DaVinci PiloT.
Provides hierarchical Bin tree navigation, Master Asset table, real-time filtering, and Asset Inspector sidebar.
"""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTreeWidget, QTreeWidgetItem,
    QSplitter, QFrame, QPushButton, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from app.models.mediapool_models import MediaPoolStructure, MediaBin, MediaAsset


class MediaPoolView(QWidget):
    """Main Media Pool & Asset Manager View Component."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._current_structure: Optional[MediaPoolStructure] = None
        self._selected_bin: Optional[MediaBin] = None
        self._all_assets: List[MediaAsset] = []
        self._displayed_assets: List[MediaAsset] = []
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header Title & Summary
        header_layout = QHBoxLayout()
        title_lbl = QLabel("Media Pool & Asset Manager")
        title_lbl.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_lbl.setStyleSheet("color: #CDD6F4;")
        header_layout.addWidget(title_lbl)

        header_layout.addStretch()

        self.summary_lbl = QLabel("Media Pool: Master | 0 Assets (0 Video / 0 Audio / 0 Image) | ⭐ 0 Good Takes")
        self.summary_lbl.setFont(QFont("Segoe UI", 10))
        self.summary_lbl.setStyleSheet("color: #A6ADC8; background-color: #181825; padding: 6px 14px; border-radius: 6px; border: 1px solid #313244;")
        header_layout.addWidget(self.summary_lbl)

        main_layout.addLayout(header_layout)

        # Filter Control Bar
        filter_card = QFrame()
        filter_card.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(12, 10, 12, 10)
        filter_layout.setSpacing(12)

        # Search Box
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("border: none; font-size: 14px;")
        filter_layout.addWidget(search_icon)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search asset name, resolution, codec, path, scene, shot, take...")
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

        # Asset Type Dropdown Filter
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Asset Types", "Video Only", "Audio Only", "Images Only", "Timelines Only"])
        self.type_filter.setStyleSheet("""
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
        self.type_filter.currentIndexChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.type_filter)

        # Good Takes Checkbox Filter
        self.good_takes_chk = QCheckBox("⭐ Good Takes Only")
        self.good_takes_chk.setStyleSheet("QCheckBox { color: #F9E2AF; font-weight: bold; font-size: 12px; border: none; }")
        self.good_takes_chk.stateChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.good_takes_chk)

        main_layout.addWidget(filter_card)

        # Splitter Layout (Left: Bin Tree, Center: Asset Table, Right: Inspector)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background-color: #313244; width: 2px; }")

        # Left Panel: Bin Folder Tree
        bin_panel = QFrame()
        bin_panel.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        bin_layout = QVBoxLayout(bin_panel)
        bin_layout.setContentsMargins(8, 8, 8, 8)

        bin_header = QLabel("📁 Bins & Folders")
        bin_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        bin_header.setStyleSheet("color: #89B4FA; padding: 4px;")
        bin_layout.addWidget(bin_header)

        self.bin_tree = QTreeWidget()
        self.bin_tree.setHeaderHidden(True)
        self.bin_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1E1E2E;
                color: #CDD6F4;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 4px;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
            }
            QTreeWidget::item:selected {
                background-color: #45475A;
                color: #89B4FA;
            }
        """)
        self.bin_tree.itemSelectionChanged.connect(self._on_bin_selected)
        bin_layout.addWidget(self.bin_tree)
        splitter.addWidget(bin_panel)

        # Center Panel: Master Asset Table
        asset_panel = QFrame()
        asset_panel.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        asset_layout = QVBoxLayout(asset_panel)
        asset_layout.setContentsMargins(8, 8, 8, 8)

        asset_header = QLabel("🎞️ Media Pool Clips")
        asset_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        asset_header.setStyleSheet("color: #CDD6F4; padding: 4px;")
        asset_layout.addWidget(asset_header)

        self.asset_table = QTableWidget()
        self.asset_table.setColumnCount(8)
        self.asset_table.setHorizontalHeaderLabels([
            "Asset Name", "Type", "Resolution", "FPS", "Duration", "Video Codec", "Audio Codec", "Good Take"
        ])
        self.asset_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.asset_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.asset_table.setStyleSheet("""
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
            QTableWidget::item:selected {
                background-color: #45475A;
                color: #FFFFFF;
            }
        """)
        self.asset_table.itemSelectionChanged.connect(self._on_asset_selected)
        asset_layout.addWidget(self.asset_table)
        splitter.addWidget(asset_panel)

        # Right Panel: Asset Inspector Sidebar
        inspector_panel = QFrame()
        inspector_panel.setStyleSheet("QFrame { background-color: #181825; border-radius: 8px; border: 1px solid #313244; }")
        inspector_layout = QVBoxLayout(inspector_panel)
        inspector_layout.setContentsMargins(12, 12, 12, 12)
        inspector_layout.setSpacing(10)

        inspector_header = QLabel("ℹ️ Asset Inspector")
        inspector_header.setFont(QFont("Segoe UI", 11, QFont.Bold))
        inspector_header.setStyleSheet("color: #F9E2AF; padding-bottom: 4px;")
        inspector_layout.addWidget(inspector_header)

        self.inspector_scroll = QScrollArea()
        self.inspector_scroll.setWidgetResizable(True)
        self.inspector_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.inspector_container = QWidget()
        self.inspector_box = QVBoxLayout(self.inspector_container)
        self.inspector_box.setContentsMargins(0, 0, 0, 0)
        self.inspector_box.setSpacing(8)
        self.inspector_box.setAlignment(Qt.AlignTop)

        self._render_empty_inspector()

        self.inspector_scroll.setWidget(self.inspector_container)
        inspector_layout.addWidget(self.inspector_scroll)
        splitter.addWidget(inspector_panel)

        # Set Splitter Ratios (Bin 20%, Table 55%, Inspector 25%)
        splitter.setSizes([220, 600, 280])

        main_layout.addWidget(splitter, 1)

    def update_mediapool_structure(self, structure: Optional[MediaPoolStructure]) -> None:
        """Update view with new MediaPoolStructure payload."""
        self._current_structure = structure

        if not structure or not structure.root_bin:
            self.summary_lbl.setText("Media Pool: Master | 0 Assets (0 Video / 0 Audio / 0 Image) | ⭐ 0 Good Takes")
            self._clear_views()
            return

        # Update Summary Bar
        self.summary_lbl.setText(
            f"Media Pool: '{structure.root_bin.name}' | {structure.total_assets} Assets "
            f"({structure.total_video_assets} Video / {structure.total_audio_assets} Audio / {structure.total_image_assets} Image) | "
            f"⭐ {structure.total_good_takes} Good Takes"
        )

        self._all_assets = structure.get_all_assets()
        self._render_bin_tree(structure.root_bin)
        self._apply_filters()

    def _clear_views(self) -> None:
        self.bin_tree.clear()
        self.asset_table.setRowCount(0)
        self._render_empty_inspector()

    def _render_bin_tree(self, root_bin: MediaBin) -> None:
        self.bin_tree.clear()

        def add_bin_item(bin_obj: MediaBin, parent_item=None) -> QTreeWidgetItem:
            item_text = f"📁 {bin_obj.name} ({bin_obj.total_assets})"
            if parent_item is None:
                tree_item = QTreeWidgetItem(self.bin_tree, [item_text])
            else:
                tree_item = QTreeWidgetItem(parent_item, [item_text])

            tree_item.setData(0, Qt.UserRole, bin_obj)

            for sub_bin in bin_obj.subfolders:
                add_bin_item(sub_bin, tree_item)

            return tree_item

        root_item = add_bin_item(root_bin)
        self.bin_tree.expandAll()
        self.bin_tree.setCurrentItem(root_item)

    def _on_bin_selected(self) -> None:
        selected_items = self.bin_tree.selectedItems()
        if selected_items:
            bin_obj = selected_items[0].data(0, Qt.UserRole)
            if isinstance(bin_obj, MediaBin):
                self._selected_bin = bin_obj
                self._apply_filters()

    def _apply_filters(self) -> None:
        query = self.search_edit.text().strip().lower()
        type_mode = self.type_filter.currentText()
        good_takes_only = self.good_takes_chk.isChecked()

        # Determine asset source pool (Selected Bin vs All Bins)
        if self._selected_bin:
            source_assets = self._selected_bin.get_all_assets()
        else:
            source_assets = self._all_assets

        filtered: List[MediaAsset] = []

        for asset in source_assets:
            # Good takes filter
            if good_takes_only and not asset.good_take:
                continue

            # Type filter
            a_type = asset.asset_type.lower()
            if type_mode == "Video Only" and "video" not in a_type:
                continue
            if type_mode == "Audio Only" and "audio" not in a_type:
                continue
            if type_mode == "Images Only" and "image" not in a_type and "still" not in a_type:
                continue
            if type_mode == "Timelines Only" and "timeline" not in a_type:
                continue

            # Text query matching
            if query:
                match = (
                    query in asset.name.lower() or
                    query in asset.resolution.lower() or
                    query in asset.video_codec.lower() or
                    query in asset.audio_codec.lower() or
                    query in asset.file_path.lower() or
                    query in asset.scene.lower() or
                    query in asset.shot.lower() or
                    query in asset.take.lower()
                )
                if not match:
                    continue

            filtered.append(asset)

        self._displayed_assets = filtered
        self._render_asset_table(filtered)

    def _render_asset_table(self, assets: List[MediaAsset]) -> None:
        self.asset_table.setRowCount(len(assets))

        for row, asset in enumerate(assets):
            good_take_badge = "⭐ Good Take" if asset.good_take else "-"
            
            self.asset_table.setItem(row, 0, QTableWidgetItem(asset.name))
            self.asset_table.setItem(row, 1, QTableWidgetItem(asset.asset_type))
            self.asset_table.setItem(row, 2, QTableWidgetItem(asset.resolution))
            self.asset_table.setItem(row, 3, QTableWidgetItem(asset.fps))
            self.asset_table.setItem(row, 4, QTableWidgetItem(asset.duration))
            self.asset_table.setItem(row, 5, QTableWidgetItem(asset.video_codec))
            self.asset_table.setItem(row, 6, QTableWidgetItem(asset.audio_codec))
            self.asset_table.setItem(row, 7, QTableWidgetItem(good_take_badge))

    def _on_asset_selected(self) -> None:
        selected_rows = self.asset_table.selectedItems()
        if selected_rows:
            row_idx = selected_rows[0].row()
            if 0 <= row_idx < len(self._displayed_assets):
                asset = self._displayed_assets[row_idx]
                self._render_inspector(asset)

    def _clear_inspector_box(self) -> None:
        while self.inspector_box.count():
            item = self.inspector_box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _render_empty_inspector(self) -> None:
        self._clear_inspector_box()
        lbl = QLabel("Select a clip to view technical metadata & production properties.")
        lbl.setWordWrap(True)
        lbl.setStyleSheet("color: #6C7086; font-style: italic; font-size: 11px;")
        self.inspector_box.addWidget(lbl)

    def _render_inspector(self, asset: MediaAsset) -> None:
        self._clear_inspector_box()

        # Asset Title
        name_lbl = QLabel(asset.name)
        name_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        name_lbl.setStyleSheet("color: #89B4FA;")
        name_lbl.setWordWrap(True)
        self.inspector_box.addWidget(name_lbl)

        # Technical Metadata Group
        def add_spec(label: str, val: str) -> None:
            row_layout = QHBoxLayout()
            l_lbl = QLabel(label)
            l_lbl.setStyleSheet("color: #A6ADC8; font-size: 11px;")
            v_lbl = QLabel(str(val))
            v_lbl.setStyleSheet("color: #CDD6F4; font-weight: bold; font-size: 11px;")
            v_lbl.setWordWrap(True)
            row_layout.addWidget(l_lbl)
            row_layout.addStretch()
            row_layout.addWidget(v_lbl)
            self.inspector_box.addLayout(row_layout)

        add_spec("Asset Type:", asset.asset_type)
        add_spec("Resolution:", asset.resolution)
        add_spec("Frame Rate:", f"{asset.fps} fps")
        add_spec("Duration:", asset.duration)
        add_spec("Video Codec:", asset.video_codec)
        add_spec("Audio Codec:", asset.audio_codec)
        add_spec("Audio Channels:", str(asset.audio_channels))
        add_spec("File Size:", asset.file_size)
        add_spec("Bin Location:", asset.bin_name)

        if asset.scene or asset.shot or asset.take:
            add_spec("Scene / Shot / Take:", f"{asset.scene} / {asset.shot} / {asset.take}")

        if asset.good_take:
            good_badge = QLabel("⭐ MARKED GOOD TAKE")
            good_badge.setStyleSheet("color: #F9E2AF; background-color: #2D4438; padding: 6px; border-radius: 4px; font-weight: bold; font-size: 11px;")
            good_badge.setAlignment(Qt.AlignCenter)
            self.inspector_box.addWidget(good_badge)

        path_lbl = QLabel(f"File Path:\n{asset.file_path}")
        path_lbl.setWordWrap(True)
        path_lbl.setStyleSheet("color: #6C7086; font-size: 10px; padding-top: 6px;")
        self.inspector_box.addWidget(path_lbl)
