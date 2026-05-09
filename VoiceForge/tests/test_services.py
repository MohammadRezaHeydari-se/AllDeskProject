from __future__ import annotations

from pathlib import Path

import pytest

from models.voice import DEFAULT_VOICE
from services.config_manager import AppConfig, ConfigManager
from services.gpu_detector import GPUDetector, GPUType


class TestConfigManager:
    def test_default_config(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"
        cm = ConfigManager(str(config_path))
        assert cm.config.default_voice == DEFAULT_VOICE
        assert cm.config.export_format == "wav"

    def test_save_and_load(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"
        cm1 = ConfigManager(str(config_path))
        cm1.set("default_voice", DEFAULT_VOICE)
        cm1.set("theme", "light")

        cm2 = ConfigManager(str(config_path))
        assert cm2.get("default_voice") == DEFAULT_VOICE
        assert cm2.get("theme") == "light"

    def test_add_recent_output(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.json"
        cm = ConfigManager(str(config_path))
        cm.add_recent_output("/path/to/file.wav")
        assert len(cm.config.recent_outputs) == 1
        cm.add_recent_output("/path/to/file.wav")
        assert len(cm.config.recent_outputs) == 1


class TestGPUDetector:
    def test_detect_returns_info(self) -> None:
        info = GPUDetector.detect()
        assert info.gpu_type in (GPUType.CUDA, GPUType.METAL, GPUType.CPU, GPUType.UNKNOWN)
        assert isinstance(info.available, bool)


if __name__ == "__main__":
    pytest.main([__file__])
