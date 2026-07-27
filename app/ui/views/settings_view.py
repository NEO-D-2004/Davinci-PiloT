"""
Settings Dialog View for DaVinci PiloT.
Allows editing app settings, NVIDIA NIM API keys (build.nvidia.com), multi-agent model mappings, DaVinci Resolve paths, and theme options.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QPushButton, QTabWidget, QWidget, QFileDialog, QGroupBox
)
from app.settings import settings_manager


class SettingsDialog(QDialog):
    """Settings Configuration Modal Dialog."""

    settings_saved = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings - DaVinci PiloT")
        self.setFixedSize(620, 520)
        self._init_ui()
        self._load_current_settings()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        tab_widget = QTabWidget(self)

        # Tab 1: NVIDIA NIM AI Configuration
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        ai_layout.setContentsMargins(16, 16, 16, 16)
        ai_layout.setSpacing(12)

        # Header Info Label
        info_lbl = QLabel("NVIDIA NIM Microservices (build.nvidia.com Free Endpoints)", ai_tab)
        info_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        info_lbl.setStyleSheet("color: #74C7EC;")
        ai_layout.addWidget(info_lbl)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

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

        # Specialized Multi-Agent Models Group Box
        models_group = QGroupBox("NVIDIA NIM Multi-Agent Routing Matrix", ai_tab)
        models_form = QFormLayout(models_group)
        models_form.setSpacing(8)

        self.input_model_planner = QLineEdit()
        self.input_model_planner.setPlaceholderText("GLM-5.2")

        self.input_model_vision = QLineEdit()
        self.input_model_vision.setPlaceholderText("MiniMax M3")

        self.input_model_reasoning = QLineEdit()
        self.input_model_reasoning.setPlaceholderText("Nemotron-3 Ultra 550B")

        self.input_model_ocr = QLineEdit()
        self.input_model_ocr.setPlaceholderText("Nemotron OCR v2")

        self.input_model_asr = QLineEdit()
        self.input_model_asr.setPlaceholderText("Nemotron ASR Streaming")

        self.input_model_embeddings = QLineEdit()
        self.input_model_embeddings.setPlaceholderText("Nemotron Embed 1B")

        models_form.addRow("Master & Planning Agent:", self.input_model_planner)
        models_form.addRow("Vision Understanding Agent:", self.input_model_vision)
        models_form.addRow("Long Reasoning Agent:", self.input_model_reasoning)
        models_form.addRow("OCR Recognition Agent:", self.input_model_ocr)
        models_form.addRow("Speech Recognition (ASR):", self.input_model_asr)
        models_form.addRow("Semantic Embeddings:", self.input_model_embeddings)

        ai_layout.addWidget(models_group)

        tab_widget.addTab(ai_tab, "🟢 NVIDIA NIM Multi-Agent")

        # Tab 2: Resolve Integration Settings
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

        # Tab 3: General Settings
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
        
        nim_models = settings_manager.get("nim_models", {})
        self.input_model_planner.setText(nim_models.get("master_planner", "GLM-5.2"))
        self.input_model_vision.setText(nim_models.get("vision", "MiniMax M3"))
        self.input_model_reasoning.setText(nim_models.get("reasoning", "Nemotron-3 Ultra 550B"))
        self.input_model_ocr.setText(nim_models.get("ocr", "Nemotron OCR v2"))
        self.input_model_asr.setText(nim_models.get("asr", "Nemotron ASR Streaming"))
        self.input_model_embeddings.setText(nim_models.get("embeddings", "Nemotron Embed 1B"))

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
        
        nim_models = {
            "master_planner": self.input_model_planner.text().strip() or "GLM-5.2",
            "vision": self.input_model_vision.text().strip() or "MiniMax M3",
            "reasoning": self.input_model_reasoning.text().strip() or "Nemotron-3 Ultra 550B",
            "ocr": self.input_model_ocr.text().strip() or "Nemotron OCR v2",
            "asr": self.input_model_asr.text().strip() or "Nemotron ASR Streaming",
            "embeddings": self.input_model_embeddings.text().strip() or "Nemotron Embed 1B",
        }
        settings_manager.set("nim_models", nim_models)

        settings_manager.set("resolve_path", self.input_resolve_path.text().strip())
        settings_manager.set("auto_connect_resolve", self.chk_auto_connect.isChecked())
        settings_manager.set("log_level", self.combo_log_level.currentText())

        self.settings_saved.emit()
        self.accept()
