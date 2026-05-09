from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from log_system.logger import LogManager
from models.voice import DEFAULT_VOICE


@dataclass
class AppConfig:
    default_output_dir: str = ""
    default_voice: str = DEFAULT_VOICE
    default_language: str = "en"
    default_speed: int = 100
    theme: str = "dark"
    export_format: str = "wav"
    max_chunk_chars: int = 300
    auto_play: bool = True
    gpu_preference: str = "auto"
    window_geometry: dict = field(default_factory=dict)
    recent_outputs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "default_output_dir": self.default_output_dir,
            "default_voice": self.default_voice,
            "default_language": self.default_language,
            "default_speed": self.default_speed,
            "theme": self.theme,
            "export_format": self.export_format,
            "max_chunk_chars": self.max_chunk_chars,
            "auto_play": self.auto_play,
            "gpu_preference": self.gpu_preference,
            "window_geometry": self.window_geometry,
            "recent_outputs": self.recent_outputs,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ConfigManager:
    _instance: ConfigManager | None = None

    def __init__(self, config_path: str | Path | None = None) -> None:
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self._default_config_path()
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load()

    @classmethod
    def initialize(cls, config_path: str | Path | None = None) -> ConfigManager:
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    @classmethod
    def get_instance(cls) -> ConfigManager:
        if cls._instance is None:
            raise RuntimeError("ConfigManager not initialized.")
        return cls._instance

    @staticmethod
    def _default_config_path() -> Path:
        return Path.home() / ".voiceforge" / "config.json"

    def _load(self) -> AppConfig:
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    data = json.load(f)
                LogManager.app(f"Config loaded from {self.config_path}")
                return AppConfig.from_dict(data)
            except (json.JSONDecodeError, OSError) as exc:
                LogManager.warning(f"Failed to load config: {exc}. Using defaults.")
        return AppConfig()

    def save(self) -> None:
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config.to_dict(), f, indent=2)
            LogManager.app(f"Config saved to {self.config_path}")
        except OSError as exc:
            LogManager.error(f"Failed to save config: {exc}")

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.config, key, default)

    def set(self, key: str, value: Any) -> None:
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save()

    def add_recent_output(self, path: str) -> None:
        if path in self.config.recent_outputs:
            self.config.recent_outputs.remove(path)
        self.config.recent_outputs.insert(0, path)
        self.config.recent_outputs = self.config.recent_outputs[:10]
        self.save()
