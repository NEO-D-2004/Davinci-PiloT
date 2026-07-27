"""
Unit tests for PySide6 UI views and MainWindow instantiation.
"""

from PySide6.QtWidgets import QApplication
from app.viewmodels import MainViewModel
from app.ui.main_window import MainWindow
from app.models.resolve_models import ResolveState, ProjectInfo


def test_ui_instantiation(qtbot):
    view_model = MainViewModel()
    window = MainWindow(viewModel=view_model)
    qtbot.addWidget(window)
    
    assert window.windowTitle() == "DaVinci PiloT - AI Copilot for DaVinci Resolve"
    assert window.isVisible() is False
    
    # Test connection finished handler with state
    mock_state = ResolveState(is_connected=True, project=ProjectInfo(name="Test Project", is_loaded=True))
    view_model._on_connection_finished(True, "Connected", mock_state)

    assert view_model.is_resolve_connected is True
    assert view_model.resolve_state.project.name == "Test Project"
