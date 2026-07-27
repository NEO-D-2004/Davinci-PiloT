"""
Unit tests for PySide6 UI views and MainWindow instantiation.
"""

import sys
from PySide6.QtWidgets import QApplication
from app.viewmodels import MainViewModel
from app.ui.main_window import MainWindow
from app.ui.splash_screen import SplashScreen


def test_ui_instantiation(qtbot):
    view_model = MainViewModel()
    window = MainWindow(viewModel=view_model)
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "DaVinci PiloT - AI Copilot for DaVinci Resolve"
    assert window.isVisible() is False
    
    # Test connection toggle
    view_model.toggle_resolve_connection()
    assert view_model.is_resolve_connected is True
