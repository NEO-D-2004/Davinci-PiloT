# Changelog - DaVinci PiloT

All notable changes to this project will be documented in this file.

## [0.2.0] - Milestone 2: DaVinci Resolve Connection (2026-07-27)

### Added
- Official DaVinci Resolve Scripting API dynamic connector (`resolve_connector.py`) loading `fusionscript.dll` and acquiring `bmd.scriptapp("Resolve")`.
- `ResolveApiWrapper` (`resolve_api.py`) providing safe queries for `ProjectManager`, `CurrentProject`, `CurrentTimeline`, and `MediaPool`.
- Data models (`resolve_models.py`) for `ProjectInfo`, `TimelineInfo`, `MediaPoolInfo`, and `ResolveState`.
- `ResolveService` high-level service layer managing connection state and diagnostics.
- Non-blocking `ResolveConnectWorker` (`QThread`) in `MainViewModel` ensuring the application UI never freezes during connection attempts.
- Live dashboard metrics synchronization in `DashboardView` displaying Active Project Title, Resolution, Frame Rate, Active Timeline Name, Video/Audio Track counts, and Clip totals.
- Action Toolbar status badge update (`● Resolve Connected` green / `● Resolve Disconnected` red).
- Dedicated unit tests for Resolve API wrapper, models, and disconnected fallbacks (`tests/test_resolve_service.py`).

---

## [0.1.0] - Milestone 1: Project Foundation (2026-07-27)

### Added
- Modular MVVM project architecture setup (`app/ui`, `app/viewmodels`, `app/services`, `app/settings`, `app/database`, `app/config`).
- PySide6 Application entry point (`app/main.py`) with High DPI support.
- Animated `SplashScreen` with step-by-step startup sequence feedback.
- Modern Dark Theme QSS stylesheet (`dark_theme.qss`).
- `Loguru` logger service integration with live Qt signal emission to UI log console and app log file rotation.
- JSON-backed `SettingsManager` for persistent user preferences.
- SQLite `DatabaseManager` for logging activity, app sessions, and history.
- NVIDIA NIM microservices integration (`build.nvidia.com`) with 7-Agent Architecture routing matrix (`GLM-5.2`, `MiniMax M3`, `Nemotron ASR`, `Nemotron OCR v2`, `Nemotron-3 Ultra 550B`, `Nemotron Embed 1B`).
- Automated `PyInstaller` build script (`build_exe.py`).
