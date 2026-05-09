from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from log_system.logger import LogManager
from log_system.rotation import RotationPolicy
from services.config_manager import ConfigManager
from services.dependency_setup import DependencySetup
from ui.main_window import MainWindow


class Application:
    def __init__(self, argv: list[str]) -> None:
        self._app = QApplication(argv)
        self._app.setApplicationName("VoiceForge")
        self._app.setOrganizationName("VoiceForge")
        self._app.setApplicationVersion("1.0.0")

        self._base_dir = Path(__file__).parent.parent
        self._log_dir = self._base_dir / "logs"

        self._init_logging()
        self._init_config()
        self._init_deps()

        self._window = MainWindow()

    def _init_logging(self) -> None:
        policy = RotationPolicy(
            daily=True,
            max_size_mb=50,
            retention_days=14,
            archive_cleanup=True,
            max_files=30,
        )
        LogManager.initialize(self._log_dir, policy)

    def _init_config(self) -> None:
        ConfigManager.initialize()

    def _init_deps(self) -> None:
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(DependencySetup.prepare_all())
            loop.close()
        except Exception as exc:
            LogManager.warning(f"Dependency setup encountered issues: {exc}")

    def run(self) -> int:
        self._window.show()
        return self._app.exec()


def main() -> int:
    app = Application(sys.argv)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
