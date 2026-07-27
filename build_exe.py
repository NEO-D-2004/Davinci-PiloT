"""
Automated PyInstaller Build Script for DaVinci PiloT.
Packages the Python PySide6 application into a standalone Windows Executable.
"""

import sys
import subprocess
from pathlib import Path


def build_executable() -> None:
    project_root = Path(__file__).resolve().parent
    spec_file = project_root / "Davinci-PiloT.spec"

    print("==================================================")
    print(" Building DaVinci PiloT Standalone Windows EXE")
    print("==================================================")

    if not spec_file.exists():
        print(f"Error: Spec file not found at {spec_file}")
        sys.exit(1)

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--clean",
        str(spec_file)
    ]

    print(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        print("\n[SUCCESS] Executable built successfully!")
        print(f"Output directory: {project_root / 'dist' / 'Davinci-PiloT'}")
    else:
        print(f"\n[ERROR] Build failed with exit code: {result.returncode}")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build_executable()
