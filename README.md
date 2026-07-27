# DaVinci PiloT

**DaVinci PiloT** is a production-quality, standalone Windows desktop application (.exe) that acts as an intelligent AI editing copilot for DaVinci Resolve using the official Resolve Scripting API.

---

## 🚀 Key Features

### Milestone 1: Project Foundation
- **Standalone Windows Executable**: Independent PySide6 Desktop Application built natively for Windows.
- **Modern Dark Theme**: Rich dark palette (`#1E1E2E`, `#181825`), clean typography, micro-animations, and responsive layout.
- **MVVM Architecture**: Clean separation between Views, ViewModels, and Services.
- **NVIDIA NIM 7-Agent Engine**: Multi-agent model router connecting to `build.nvidia.com` free endpoints (`GLM-5.2`, `MiniMax M3`, `Nemotron ASR`, `Nemotron OCR v2`, `Nemotron-3 Ultra 550B`, `Nemotron Embed 1B`).
- **FFmpeg Frame Sampling**: 1.0 FPS & scene boundary keyframe extraction strategy preventing raw long video payloads to LLMs.

### Milestone 2: DaVinci Resolve Connection
- **Official Resolve Scripting API loader**: Dynamic loading of `fusionscript.dll` and `DaVinciResolveScript` module (`bmd.scriptapp("Resolve")`).
- **Process & Instance Detection**: Checks if `Resolve.exe` is running on Windows and handles missing application handles gracefully.
- **Current Project & Timeline Queries**: Live querying of Active Project Name, Resolution, Frame Rate, Timelines Count, Active Timeline Name, Video/Audio Tracks Count, and Total Clips.
- **Zero-Click Local Bridge HTTP Server**: `http://127.0.0.1:18888` server accepting real-time state payloads from `DaVinciPiloT_Bridge` script inside DaVinci Resolve 21 Free & Studio.

### Milestone 3: Timeline Explorer
- **Deep Timeline Structure Parsing**: Extracts Video/Audio Tracks (`V1`, `V2`, `A1`...), Clip items (`start_frame`, `end_frame`, `duration_frames`, `left_offset`, `right_offset`), Media Pool source file paths, flag colors, and clip colors.
- **Interactive Visual Track Lanes**: Stacked track view displaying color-coded clip blocks with hover tooltips and clip duration indicators.
- **Master Clip Table**: Searchable and filterable master table displaying Clip Name, Track, Start-End Frames, Duration, Source File Path, and Flags.
- **Timeline Markers Panel**: Detailed table of timeline markers displaying frame indices, timecodes, color badges, marker names, and notes.
- **Real-Time Clip Filter Engine**: Instant client-side search box and track filter dropdowns (All Tracks, Video Only, Audio Only).

---

## 🛠️ Tech Stack

- **Language**: Python 3.13+
- **GUI Framework**: PySide6 (Qt 6)
- **Architecture**: MVVM (Model-View-ViewModel)
- **Automation**: DaVinci Resolve Scripting API (`fusionscript.dll` & HTTP Bridge)
- **AI Infrastructure**: NVIDIA NIM Microservices (`build.nvidia.com`)
- **Database**: SQLite (`app.db`)
- **Configuration & Settings**: `.env` & JSON (`user_settings.json`)
- **Logging**: Loguru
- **Packaging**: PyInstaller

---

## 📦 Project Structure

```
Davinci-PiloT/
├── app/
│   ├── ai/
│   │   ├── agent_router.py
│   │   ├── frame_sampler.py
│   │   ├── nim_client.py
│   │   └── pipeline.py
│   ├── assets/styles/dark_theme.qss
│   ├── automation/
│   │   ├── bridge_installer.py
│   │   ├── bridge_server.py
│   │   ├── resolve_api.py
│   │   └── resolve_connector.py
│   ├── config/config_loader.py
│   ├── database/db_manager.py
│   ├── models/
│   │   ├── resolve_models.py
│   │   └── timeline_models.py
│   ├── services/
│   │   ├── logger_service.py
│   │   └── resolve_service.py
│   ├── settings/settings_manager.py
│   ├── ui/
│   │   ├── components/
│   │   │   ├── menu_bar.py
│   │   │   ├── notification_center.py
│   │   │   ├── status_bar.py
│   │   │   └── toolbar.py
│   │   ├── views/
│   │   │   ├── dashboard_view.py
│   │   │   ├── settings_view.py
│   │   │   └── timeline_view.py
│   │   ├── main_window.py
│   │   └── splash_screen.py
│   ├── viewmodels/main_viewmodel.py
│   └── main.py
├── tests/
│   ├── test_ai.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_resolve_service.py
│   ├── test_settings.py
│   ├── test_timeline.py
│   └── test_ui.py
├── .env.example
├── build_exe.py
├── Davinci-PiloT.spec
├── requirements.txt
└── README.md
```

---

## 💻 How to Run

### 1. Virtual Environment Setup
```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

### 2. Run Desktop Application
```bash
.venv\Scripts\python app\main.py
```

### 3. Run Automated Unit Tests
```bash
.venv\Scripts\pytest tests/
```

### 4. Build Standalone Executable (.exe)
```bash
.venv\Scripts\python build_exe.py
```
Output executable: `dist/Davinci-PiloT/Davinci-PiloT.exe`.
