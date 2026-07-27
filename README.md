# DaVinci PiloT

**DaVinci PiloT** is a production-quality, standalone Windows desktop application (.exe) that acts as an intelligent AI editing copilot for DaVinci Resolve using the official Resolve Scripting API.

---

## 🚀 Key Features (Milestone 1)

- **Standalone Windows Executable**: Independent PySide6 Desktop Application built natively for Windows.
- **Modern Dark Theme**: Rich dark palette (`#1E1E2E`, `#181825`), clean typography, micro-animations, and responsive layout.
- **MVVM Architecture**: Clean separation between Views, ViewModels, and Services.
- **Core Services**:
  - `LoggerService`: Powered by Loguru with console, file rotation, and Qt live signal routing.
  - `SettingsManager`: JSON-backed persistent preferences with Qt signal bindings.
  - `DatabaseManager`: Local SQLite database tracking sessions and activity logs.
- **UI Components**: MenuBar, Action Toolbar with status badges, Status Bar, Notification Toast system, and Dashboard workspace.
- **Splash Screen**: Animated loading splash screen during startup sequence.
- **PyInstaller Packaging**: Automated script (`build_exe.py`) producing standalone `Davinci-PiloT.exe`.

---

## 🛠️ Tech Stack

- **Language**: Python 3.13+
- **GUI Framework**: PySide6 (Qt 6)
- **Architecture**: MVVM (Model-View-ViewModel)
- **Database**: SQLite
- **Configuration & Settings**: `.env` & JSON (`user_settings.json`)
- **Logging**: Loguru
- **Packaging**: PyInstaller

---

## 📦 Project Structure

```
Davinci-PiloT/
├── app/
│   ├── assets/
│   │   └── styles/
│   │       └── dark_theme.qss
│   ├── config/
│   │   └── config_loader.py
│   ├── database/
│   │   └── db_manager.py
│   ├── logs/
│   │   └── app.log
│   ├── services/
│   │   └── logger_service.py
│   ├── settings/
│   │   └── settings_manager.py
│   ├── ui/
│   │   ├── components/
│   │   │   ├── menu_bar.py
│   │   │   ├── notification_center.py
│   │   │   ├── status_bar.py
│   │   │   └── toolbar.py
│   │   ├── views/
│   │   │   ├── dashboard_view.py
│   │   │   └── settings_view.py
│   │   ├── main_window.py
│   │   └── splash_screen.py
│   ├── utils/
│   ├── viewmodels/
│   │   └── main_viewmodel.py
│   └── main.py
├── tests/
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_settings.py
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
The output executable will be created in `dist/Davinci-PiloT/Davinci-PiloT.exe`.
