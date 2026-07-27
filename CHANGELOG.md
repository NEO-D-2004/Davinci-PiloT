# Changelog - DaVinci PiloT

All notable changes to this project will be documented in this file.

## [0.1.0] - Milestone 1: Project Foundation (2026-07-27)

### Added
- Modular MVVM project architecture setup (`app/ui`, `app/viewmodels`, `app/services`, `app/settings`, `app/database`, `app/config`).
- PySide6 Application entry point (`app/main.py`) with High DPI support.
- Animated `SplashScreen` with step-by-step startup sequence feedback.
- Modern Dark Theme QSS stylesheet (`dark_theme.qss`) featuring dark slate palette, high-contrast typography, and styled widgets.
- `Loguru` logger service integration with live Qt signal emission to UI log console and app log file rotation.
- JSON-backed `SettingsManager` for persistent user preferences with signal bindings.
- SQLite `DatabaseManager` for logging activity, app sessions, and history.
- Application UI layout:
  - Custom `AppMenuBar` with File, Edit, View, Resolve, AI, Tools, and Help menus.
  - Action `AppToolBar` with Resolve connection toggles and status indicators.
  - Interactive `AppStatusBar` displaying live messages, task progress bar, and active AI badge.
  - Non-intrusive floating `NotificationCenter` toast overlay for Info, Success, Warning, and Error messages.
  - `DashboardView` with system status metrics cards and live activity log console.
  - Tabbed `SettingsDialog` for AI API keys, DaVinci Resolve scripting paths, and log preferences.
- Automated `PyInstaller` build script (`build_exe.py`) and spec file (`Davinci-PiloT.spec`).
- Unit test suite covering configuration, settings, database, and PySide6 UI views (`tests/`).
