# Changelog - DaVinci PiloT

All notable changes to this project will be documented in this file.

## [0.5.0] - Milestone 5: NVIDIA NIM Multi-Agent Vision & Audio Analyzer (2026-07-28)

### Added
- Analyzer Data Models (`analyzer_models.py`): `TranscriptSegment`, `SilenceGap`, `VisualFrameInsight`, `SmartCutProposal`, `AnalysisReport`.
- Speech & Silence Analysis Engine (`AudioAnalyzer` in `analyzer_engine.py`): Speech-to-text transcription via `Nemotron ASR`, filler word detection ("um", "uh"), and silence gap identification (> 1.2s pauses).
- Multimodal Vision Analysis Engine (`VisionAnalyzer` in `analyzer_engine.py`): Keyframe sampling via `FrameSampler` and visual scene understanding via `MiniMax M3`.
- Multi-Agent Orchestrator Pipeline (`MultiAgentAnalyzer` in `multi_agent_pipeline.py`): Connects `Nemotron ASR`, `MiniMax M3`, and `GLM-5.2` Master Agent to synthesize visual & audio insights into `SmartCutProposal` recommendations.
- Interactive `AnalyzerView` UI component with 3 tabs:
  - **🗣️ Speech & Silence**: Timestamped transcript segments table and silence gap cards.
  - **👁️ Vision Keyframes (MiniMax M3)**: Table detailing keyframes, timecodes, scene descriptions, and camera motion.
  - **✂️ Smart Cut Proposals (GLM-5.2)**: Prioritized edit proposals (Silence cuts, filler removals, scene transitions).
- Non-blocking background analysis execution worker thread (`AnalyzerWorkerThread`).
- Tab bar integration in `MainWindow` featuring **🤖 AI Analyzer**.
- Comprehensive unit test suite for Analyzer models, engines, pipeline, and UI view rendering (`tests/test_analyzer.py`).

---

## [0.4.0] - Milestone 4: Media Pool & Asset Manager (2026-07-28)

### Added
- Media Pool Data Models (`mediapool_models.py`): `MediaAsset`, `MediaBin`, `MediaPoolStructure`.
- Recursive Media Pool Bins and Clip Metadata extractor in `DaVinciPiloT_Bridge.py` extracting Bins, Subfolders, Clip Properties (File Path, Resolution, FPS, Duration, Video/Audio Codecs, Channels, File Size, Date Modified), and User Metadata (Scene, Shot, Take, Good Take, Comments).
- Media Pool Structure JSON parser (`parse_mediapool_structure`) in `bridge_server.py`.
- Interactive `MediaPoolView` UI component featuring Bin Folder Tree, Master Asset Table, Asset Inspector Sidebar, and Multi-Criteria Asset Filters.

---

## [0.3.0] - Milestone 3: Timeline Explorer (2026-07-28)

### Added
- Timeline Data Models (`timeline_models.py`): `ClipItem`, `TrackInfo`, `TimelineMarker`, `TimelineStructure`.
- Detailed DaVinci Resolve 21 Timeline Structure extractor in `DaVinciPiloT_Bridge.py`.
- Interactive `TimelineView` UI component featuring Visual Track Lanes, Clip Master Table, and Markers Panel.

---

## [0.2.0] - Milestone 2: DaVinci Resolve Connection (2026-07-27)

### Added
- Official DaVinci Resolve Scripting API dynamic connector (`resolve_connector.py`) loading `fusionscript.dll`.
- Real-time zero-click local HTTP server (`bridge_server.py`) on `http://127.0.0.1:18888`.
- Auto-deployed DaVinci PiloT Bridge script (`bridge_installer.py`).

---

## [0.1.0] - Milestone 1: Project Foundation (2026-07-27)

### Added
- Modular MVVM project architecture setup (`app/ui`, `app/viewmodels`, `app/services`, `app/settings`, `app/database`, `app/config`).
- PySide6 Application entry point (`app/main.py`) with High DPI support.
- NVIDIA NIM microservices integration (`build.nvidia.com`) with 7-Agent Architecture routing matrix.
- Automated `PyInstaller` build script (`build_exe.py`).
