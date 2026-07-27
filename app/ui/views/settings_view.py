"""
Settings Dialog View for DaVinci PiloT.
Allows editing app settings, NVIDIA NIM API keys (build.nvidia.com), 7-Agent Model Mappings, Frame Sampling parameters, and Resolve paths.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QPushButton, QTabWidget, QWidget, QFileDialog, QGroupBox, QDoubleSpinBox
)
from app.settings import settings_manager


class SettingsDialog(QDialog):
    """Settings Configuration Modal Dialog."""

    settings_saved = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings - DaVinci PiloT")
        self.setFixedSize(680, 560)
        self._init_ui()
        self._load_current_settings()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        tab_widget = QTabWidget(self)

        # Tab 1: NVIDIA NIM 7-Agent Architecture
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        ai_layout.setContentsMargins(16, 16, 16, 16)
        ai_layout.setSpacing(10)

        info_lbl = QLabel("NVIDIA NIM Microservices (build.nvidia.com 7-Agent Pipeline)", ai_tab)
        info_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        info_lbl.setStyleSheet("color: #74C7EC;")
        ai_layout.addWidget(info_lbl)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)

        self.combo_ai_provider = QComboBox()
        self.combo_ai_provider.addItems(["nvidia_nim", "gemini", "openai", "local_llm"])

        self.input_nvidia_key = QLineEdit()
        self.input_nvidia_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nvidia_key.setPlaceholderText("Enter NVIDIA NIM API Key (build.nvidia.com)")

        self.input_nvidia_url = QLineEdit()
        self.input_nvidia_url.setPlaceholderText("https://integrate.api.nvidia.com/v1")

        form_layout.addRow("Active AI Provider:", self.combo_ai_provider)
        form_layout.addRow("NVIDIA NIM API Key:", self.input_nvidia_key)
        form_layout.addRow("NVIDIA NIM Base URL:", self.input_nvidia_url)

        ai_layout.addLayout(form_layout)

        # Specialized 7-Agent Model Matrix Group Box
        models_group = QGroupBox("Specialized 7-Agent Routing Matrix", ai_tab)
        models_form = QFormLayout(models_group)
        models_form.setSpacing(6)

        self.input_agent_master = QLineEdit()
        self.input_agent_master.setPlaceholderText("GLM-5.2")

        self.input_agent_vision = QLineEdit()
        self.input_agent_vision.setPlaceholderText("MiniMax M3")

        self.input_agent_speech = QLineEdit()
        self.input_agent_speech.setPlaceholderText("Nemotron ASR Streaming")

        self.input_agent_ocr = QLineEdit()
        self.input_agent_ocr.setPlaceholderText("Nemotron OCR v2")

        self.input_agent_story = QLineEdit()
        self.input_agent_story.setPlaceholderText("GLM-5.2")

        self.input_agent_planner = QLineEdit()
        self.input_agent_planner.setPlaceholderText("Nemotron-3 Ultra 550B")

        self.input_agent_resolve = QLineEdit()
        self.input_agent_resolve.setPlaceholderText("Deterministic DaVinci API Translator")
        self.input_agent_resolve.setReadOnly(True)

        models_form.addRow("1. Master Agent (Orchestration):", self.input_agent_master)
        models_form.addRow("2. Vision Agent (Sampled Frames):", self.input_agent_vision)
        models_form.addRow("3. Speech Agent (ASR & Speakers):", self.input_agent_speech)
        models_form.addRow("4. OCR Agent (Slides & Text):", self.input_agent_ocr)
        models_form.addRow("5. Story Agent (Multi-Modal Arc):", self.input_agent_story)
        models_form.addRow("6. Editing Planner (Timeline Plan):", self.input_agent_planner)
        models_form.addRow("7. Resolve Agent (API Executor):", self.input_agent_resolve)

        ai_layout.addWidget(models_group)

        tab_widget.addTab(ai_tab, "🤖 7-Agent Architecture")

        # Tab 2: Frame Sampling & Extraction Strategy
        sampling_tab = QWidget()
        sampling_layout = QFormLayout(sampling_tab)
        sampling_layout.setContentsMargins(16, 16, 16, 16)
        sampling_layout.setSpacing(12)

        s_info = QLabel("FFmpeg Frame & Audio Sampling Strategy (Prevents Sending Raw Video to LLMs)", sampling_tab)
        s_info.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        s_info.setStyleSheet("color: #89B4FA;")
        sampling_layout.addRow(s_info)

        self.spin_fps = QDoubleSpinBox()
        self.spin_fps.setRange(0.1, 30.0)
        self.spin_fps.setSingleStep(0.5)
        self.spin_fps.setValue(1.0)
        self.spin_fps.setSuffix(" FPS")

        self.chk_detect_scenes = QCheckBox("Automatically detect scene boundaries for keyframe extraction")
        self.input_ffmpeg = QLineEdit()
        self.input_ffmpeg.setPlaceholderText("ffmpeg")

        sampling_layout.addRow("Frame Extraction Rate:", self.spin_fps)
        sampling_layout.addRow("Scene Boundary Detection:", self.chk_detect_scenes)
        sampling_layout.addRow("FFmpeg Binary Path:", self.input_ffmpeg)

        tab_widget.addTab(sampling_tab, "🎞️ Frame Sampling")

        # Tab 3: Resolve Integration Settings
        resolve_tab = QWidget()
        resolve_layout = QFormLayout(resolve_tab)
        resolve_layout.setContentsMargins(16, 16, 16, 16)
        resolve_layout.setSpacing(12)

        path_layout = QHBoxLayout()
        self.input_resolve_path = QLineEdit()
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_resolve_path)
        path_layout.addWidget(self.input_resolve_path)
        path_layout.addWidget(btn_browse)

        self.chk_auto_connect = QCheckBox("Auto-connect to Resolve on application launch")

        resolve_layout.addRow("Scripting API Path:", path_layout)
        resolve_layout.addRow("", self.chk_auto_connect)

        tab_widget.addTab(resolve_tab, "🎬 DaVinci Resolve")

        # Tab 4: General Settings
        gen_tab = QWidget()
        gen_layout = QFormLayout(gen_tab)
        gen_layout.setContentsMargins(16, 16, 16, 16)
        gen_layout.setSpacing(12)

        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["dark"])

        self.combo_log_level = QComboBox()
        self.combo_log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])

        gen_layout.addRow("UI Theme:", self.combo_theme)
        gen_layout.addRow("Log Level:", self.combo_log_level)

        tab_widget.addTab(gen_tab, "⚙️ General")

        layout.addWidget(tab_widget)

        # Dialog Action Buttons
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel", self)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Settings", self)
        btn_save.setStyleSheet("background-color: #89B4FA; color: #11111B;")
        btn_save.clicked.connect(self._save_settings)

        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)

        layout.addLayout(btn_box)

    def _load_current_settings(self) -> None:
        """Populate fields with current settings."""
        self.combo_ai_provider.setCurrentText(settings_manager.get("ai_provider", "nvidia_nim"))
        self.input_nvidia_key.setText(settings_manager.get("nvidia_nim_api_key", ""))
        self.input_nvidia_url.setText(settings_manager.get("nvidia_nim_base_url", "https://integrate.api.nvidia.com/v1"))
        
        matrix = settings_manager.get("agent_matrix", {})
        self.input_agent_master.setText(matrix.get("master_agent", "GLM-5.2"))
        self.input_agent_vision.setText(matrix.get("vision_agent", "MiniMax M3"))
        self.input_agent_speech.setText(matrix.get("speech_agent", "Nemotron ASR Streaming"))
        self.input_agent_ocr.setText(matrix.get("ocr_agent", "Nemotron OCR v2"))
        self.input_agent_story.setText(matrix.get("story_agent", "GLM-5.2"))
        self.input_agent_planner.setText(matrix.get("editing_planner", "Nemotron-3 Ultra 550B"))

        fs = settings_manager.get("frame_sampling", {})
        self.spin_fps.setValue(fs.get("sample_rate_fps", 1.0))
        self.chk_detect_scenes.setChecked(fs.get("detect_scene_changes", True))
        self.input_ffmpeg.setText(fs.get("ffmpeg_path", "ffmpeg"))

        self.input_resolve_path.setText(settings_manager.get("resolve_path", ""))
        self.chk_auto_connect.setChecked(settings_manager.get("auto_connect_resolve", True))
        self.combo_log_level.setCurrentText(settings_manager.get("log_level", "INFO"))

    def _browse_resolve_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select Resolve Scripting Directory")
        if path:
            self.input_resolve_path.setText(path)

    def _save_settings(self) -> None:
        """Save dialog state to settings manager."""
        settings_manager.set("ai_provider", self.combo_ai_provider.currentText())
        settings_manager.set("nvidia_nim_api_key", self.input_nvidia_key.text().strip())
        settings_manager.set("nvidia_nim_base_url", self.input_nvidia_url.text().strip())
        
        agent_matrix = {
            "master_agent": self.input_agent_master.text().strip() or "GLM-5.2",
            "vision_agent": self.input_agent_vision.text().strip() or "MiniMax M3",
            "speech_agent": self.input_agent_speech.text().strip() or "Nemotron ASR Streaming",
            "ocr_agent": self.input_agent_ocr.text().strip() or "Nemotron OCR v2",
            "story_agent": self.input_agent_story.text().strip() or "GLM-5.2",
            "editing_planner": self.input_agent_planner.text().strip() or "Nemotron-3 Ultra 550B",
            "resolve_agent": "Deterministic DaVinci API Translator"
        }
        settings_manager.set("agent_matrix", agent_matrix)

        frame_sampling = {
            "sample_rate_fps": self.spin_fps.value(),
            "detect_scene_changes": self.chk_detect_scenes.isChecked(),
            "ffmpeg_path": self.input_ffmpeg.text().strip() or "ffmpeg"
        }
        settings_manager.set("frame_sampling", frame_sampling)

        settings_manager.set("resolve_path", self.input_resolve_path.text().strip())
        settings_manager.set("auto_connect_resolve", self.chk_auto_connect.isChecked())
        settings_manager.set("log_level", self.combo_log_level.currentText())

        self.settings_saved.emit()
        self.accept()
