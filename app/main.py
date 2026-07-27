"""
Application Entry Point for DaVinci PiloT.
Initializes PySide6 Application, displays Splash Screen, loads core services, and launches MainWindow.
"""

import sys
import time
from pathlib import Path

# Ensure project root is in sys.path when running app/main.py directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication
from app.ui.splash_screen import SplashScreen
from app.ui.main_window import MainWindow
from app.viewmodels import MainViewModel
from app.services.logger_service import app_logger
from app.settings import settings_manager
from app.database import db_manager


def main() -> None:
    # High DPI scaling configuration
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("DaVinci PiloT")
    app.setOrganizationName("DaVinci PiloT")

    # Display Splash Screen
    splash = SplashScreen()
    splash.show()
    app.processEvents()

    # Step 1: Initialize Logging & Config
    splash.set_progress(25, "Initializing logging & environment configuration...")
    app_logger.info("Initializing DaVinci PiloT startup sequence...")
    time.sleep(0.3)
    app.processEvents()

    # Step 2: Initialize Settings Manager
    splash.set_progress(50, "Loading JSON settings & preferences...")
    _ = settings_manager.get_all()
    time.sleep(0.3)
    app.processEvents()

    # Step 3: Initialize SQLite Database
    splash.set_progress(75, "Connecting to SQLite database storage...")
    db_manager.log_activity(
        level="INFO",
        category="APP_START",
        message="Application launched successfully",
        details="Milestone 1 execution"
    )
    time.sleep(0.3)
    app.processEvents()

    # Step 4: Instantiating MVVM ViewModel & Main Window
    splash.set_progress(95, "Setting up PySide6 MVVM User Interface...")
    view_model = MainViewModel()
    main_window = MainWindow(viewModel=view_model)
    time.sleep(0.2)
    app.processEvents()

    # Transition from Splash to Main Window
    splash.set_progress(100, "Ready!")
    splash.finish(main_window)
    main_window.show()

    app_logger.info("DaVinci PiloT desktop application running.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
