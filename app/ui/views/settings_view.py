"""
Settings Dialog View for DaVinci PiloT.
Allows editing app settings, AI API keys, DaVinci Resolve paths, and theme options.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QComboBox, QCheckBox, QPushButton, QTabWidget, QWidget, QFileDialog
)
from app.settings import settings_manager


class SettingsDialog(QDialog):
    """Settings Configuration Modal Dialog."""

    settings_saved = Signal()

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings - DaVinci PiloT")
        self.setFixedSize(540, 420)
        self._init_ui()
        self._load_current_settings()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        tab_widget = QTabWidget(self)

        # Tab 1: AI Provider Settings
        ai_tab = QWidget()
        ai_layout = QFormLayout(ai_tab)
        ai_layout.setContentsMargins(16, 16, 16, 16)
        ai_layout.setSpacing(12)

        self.combo_ai_provider = QComboBox()
        self.combo_ai_provider.addItems(["gemini", "nvidia_nim", "openai", "local_llm"])

        self.input_gemini_key = QLineEdit()
        self.input_gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_gemini_key.setPlaceholderText("Enter Gemini API Key")

        self.input_nvidia_key = QLineEdit()
        self.input_nvidia_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_nvidia_key.setPlaceholderText("Enter NVIDIA NIM API Key")

        self.input_openai_key = QLineEdit()
        self.input_openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_openai_key.setPlaceholderText("Enter OpenAI API Key")

        self.input_local_llm_url = QLineEdit()
        self.input_local_llm_url.setPlaceholderText("http://localhost:11434/v1")

        ai_layout.addRow("Default AI Provider:", self.combo_ai_provider)
        ai_layout.addRow("Gemini API Key:", self.input_gemini_key)
        ai_layout.addRow("NVIDIA NIM Key:", self.input_nvidia_key)
        ai_layout.addRow("OpenAI API Key:", self.input_openai_key)
        ai_layout.addRow("Local LLM Endpoint:", self.input_local_llm_url)

        tab_widget.addTab(ai_tab, "🤖 AI Configuration")

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
        self.combo_ai_provider.setCurrentText(settings_manager.get("ai_provider", "gemini"))
        self.input_gemini_key.setText(settings_manager.get("gemini_api_key", ""))
        self.input_nvidia_key.setText(settings_manager.get("nvidia_nim_api_key", ""))
        self.input_openai_key.setText(settings_manager.get("openai_api_key", ""))
        self.input_local_llm_url.setText(settings_manager.get("local_llm_url", "http://localhost:11434/v1"))
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
        settings_manager.set("gemini_api_key", self.input_gemini_key.text().strip())
        settings_manager.set("nvidia_nim_api_key", self.input_nvidia_key.text().strip())
        settings_manager.set("openai_api_key", self.input_openai_key.text().strip())
        settings_manager.set("local_llm_url", self.input_local_llm_url.text().strip())
        settings_manager.set("resolve_path", self.input_resolve_path.text().strip())
        settings_manager.set("auto_connect_resolve", self.chk_auto_connect.isChecked())
        settings_manager.set("log_level", self.combo_log_level.currentText())

        self.settings_saved.emit()
        self.accept()
