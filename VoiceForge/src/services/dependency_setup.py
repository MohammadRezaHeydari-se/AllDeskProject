from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

from log_system.logger import LogManager


class DependencySetup:
    SYSTEM = platform.system()

    @classmethod
    async def prepare_all(cls) -> dict[str, bool]:
        results: dict[str, bool] = {}
        results["ffmpeg"] = cls._check_ffmpeg()
        results["python_deps"] = cls._install_python_deps()
        results["system_deps"] = cls._install_system_deps()
        return results

    @classmethod
    def _check_ffmpeg(cls) -> bool:
        if shutil.which("ffmpeg"):
            LogManager.app("ffmpeg found on system")
            return True
        LogManager.warning("ffmpeg not found. Audio processing may be limited.")

        if cls.SYSTEM == "Linux":
            cls._run(["apt-get", "install", "-y", "ffmpeg"]) if shutil.which("apt-get") else None
        elif cls.SYSTEM == "Darwin":
            cls._run(["brew", "install", "ffmpeg"]) if shutil.which("brew") else None
        elif cls.SYSTEM == "Windows":
            LogManager.app("Windows: ffmpeg must be downloaded manually or added to PATH")

        return shutil.which("ffmpeg") is not None

    @classmethod
    def _install_python_deps(cls) -> bool:
        try:
            req_file = Path(__file__).parent.parent / "requirements.txt"
            if req_file.exists():
                cls._run([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
                LogManager.app("Python dependencies installed")
                return True
        except Exception as exc:
            LogManager.error(f"Failed to install Python deps: {exc}")
        return False

    @classmethod
    def _install_system_deps(cls) -> bool:
        if cls.SYSTEM == "Linux":
            try:
                cls._run(["apt-get", "update", "-qq"])
                for pkg in ["libportaudio2", "libsndfile1", "espeak-ng"]:
                    cls._run(["apt-get", "install", "-y", "-qq", pkg])
                return True
            except Exception as exc:
                LogManager.warning(f"System deps install failed: {exc}")
                return False
        return True

    @staticmethod
    def _run(cmd: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120)
