# Changelog - DaVinci PiloT

All notable changes to this project will be documented in this file.

## [0.4.0] - Milestone 4: Media Pool & Asset Manager (2026-07-28)

### Added
- Media Pool Data Models (`mediapool_models.py`): `MediaAsset`, `MediaBin`, `MediaPoolStructure`.
- Recursive Media Pool Bins and Clip Metadata extractor in `DaVinciPiloT_Bridge.py` extracting Bins, Subfolders, Clip Properties (File Path, Resolution, FPS, Duration, Video/Audio Codecs, Channels, File Size, Date Modified), and User Metadata (Scene, Shot, Take, Good Take, Comments).
- Media Pool Structure JSON parser (`parse_mediapool_structure`) in `bridge_server.py`.
- Interactive `MediaPoolView` UI component featuring:
  - **Hierarchical Bin Folder Tree**: Folder tree sidebar displaying Bins (`Master`, `B-Roll`, `Audio`...) with clip counters.
  - **Master Asset Table**: Searchable and filterable table displaying Asset Name, Type, Resolution, FPS, Duration, Video Codec, Audio Codec, and Good Take badges.
  - **Asset Inspector Sidebar**: Right panel rendering technical specs and production metadata notes.
  - **Multi-Criteria Asset Filters**: Instant search box, type filter dropdown ("All Asset Types", "Video Only", "Audio Only", "Images Only", "Timelines Only"), and "⭐ Good Takes Only" toggle.
- Tab bar integration in `MainWindow` featuring **📁 Media Pool Manager**.
- Comprehensive unit test suite for Media Pool models, JSON parser, and UI view rendering (`tests/test_mediapool.py`).

---

## [0.3.0] - Milestone 3: Timeline Explorer (2026-07-28)

### Added
- Timeline Data Models (`timeline_models.py`): `ClipItem`, `TrackInfo`, `TimelineMarker`, `TimelineStructure`.
- Detailed DaVinci Resolve 21 Timeline Structure extractor in `DaVinciPiloT_Bridge.py` extracting Video/Audio tracks, Clip items, start/end frames, durations, trim handles, Media Pool source file paths, flag colors, and clip colors.
- Timeline Structure parser (`parse_timeline_structure`) in `bridge_server.py`.
- Interactive `TimelineView` UI component with 3 tabs:
  - **Visual Track Lanes**: Interactive horizontal track lanes (`V1`, `V2`, `A1`, `A2`...) displaying color-coded clip blocks with hover tooltips.
  - **Clip Master Table**: Searchable and filterable master table detailing Clip Name, Track, Start-End Frames, Duration, Source File Path, and Flags.
  - **Markers & Notes Panel**: Detailed table of timeline markers with color badges, frame timecode, names, and notes.
- Real-time search box and track filter dropdowns ("All Tracks", "Video Tracks Only", "Audio Tracks Only").
- Central tab container (`QTabWidget`) in `MainWindow` linking **Command Center** and **Timeline Explorer**.
- Dedicated unit tests for Timeline models, JSON parser, and UI view rendering (`tests/test_timeline.py`).

---

## [0.2.0] - Milestone 2: DaVinci Resolve Connection (2026-07-27)

### Added
- Official DaVinci Resolve Scripting API dynamic connector (`resolve_connector.py`) loading `fusionscript.dll` and acquiring `bmd.scriptapp("Resolve")`.
- Real-time zero-click local HTTP server (`bridge_server.py`) on `http://127.0.0.1:18888`.
- Auto-deployed DaVinci PiloT Bridge script (`bridge_installer.py`) enabling instant connection for DaVinci Resolve 21 Free & Studio.
- `ResolveApiWrapper` (`resolve_api.py`) providing safe queries for `ProjectManager`, `CurrentProject`, `CurrentTimeline`, and `MediaPool`.
- Non-blocking `ResolveConnectWorker` (`QThread`) in `MainViewModel`.
- Live dashboard metrics synchronization in `DashboardView` and Action Toolbar status badge update (`● Resolve Connected` green / `● Resolve Disconnected` red).

---

## [0.1.0] - Milestone 1: Project Foundation (2026-07-27)

### Added
- Modular MVVM project architecture setup (`app/ui`, `app/viewmodels`, `app/services`, `app/settings`, `app/database`, `app/config`).
- PySide6 Application entry point (`app/main.py`) with High DPI support.
- Animated `SplashScreen` with step-by-step startup sequence feedback.
- Modern Dark Theme QSS stylesheet (`dark_theme.qss`).
- NVIDIA NIM microservices integration (`build.nvidia.com`) with 7-Agent Architecture routing matrix (`GLM-5.2`, `MiniMax M3`, `Nemotron ASR`, `Nemotron OCR v2`, `Nemotron-3 Ultra 550B`, `Nemotron Embed 1B`).
- Automated `PyInstaller` build script (`build_exe.py`).
