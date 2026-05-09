from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from .rotation import RotationPolicy
from .sanitizer import LogSanitizer


def _build_extra(record: dict[str, Any]) -> dict[str, Any]:
    extra = {
        "os": platform.system(),
        "os_version": platform.version(),
    }
    extra.update(LogSanitizer.sanitize_record(record.get("extra", {})))
    return extra


class JsonSink:
    def __init__(self, log_file: Path) -> None:
        self.log_file = log_file

    def write(self, message: Any) -> None:
        record = message.record
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record["level"].name,
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": LogSanitizer.sanitize(str(record["message"])),
            **_build_extra(record),
        }
        if record["level"].no >= 40:
            log_entry["exception"] = str(record.get("exception") or "")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, default=str) + "\n")


class LogManager:
    _instance: LogManager | None = None

    def __init__(self, log_dir: str | Path, policy: RotationPolicy | None = None) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.policy = policy or RotationPolicy()
        self._sinks: list[int] = []
        self._setup_sinks()

    @classmethod
    def initialize(cls, log_dir: str | Path, policy: RotationPolicy | None = None) -> LogManager:
        if cls._instance is None:
            cls._instance = cls(log_dir, policy)
        return cls._instance

    @classmethod
    def get_instance(cls) -> LogManager:
        if cls._instance is None:
            raise RuntimeError("LogManager not initialized. Call LogManager.initialize() first.")
        return cls._instance

    def _setup_sinks(self) -> None:
        logger.remove()

        # Use serialize=True for file sinks to get proper rotation support
        # Each sink writes loguru's native JSON format
        self._sinks.append(logger.add(
            self.log_dir / "app.log",
            serialize=True,
            level="DEBUG",
            rotation=self.policy.rotation_size,
            retention=f"{self.policy.retention_days} days",
            compression="gz",
            filter=self._app_filter,
        ))

        self._sinks.append(logger.add(
            self.log_dir / "crash.log",
            serialize=True,
            level="ERROR",
            rotation=self.policy.rotation_size,
            retention=f"{self.policy.retention_days} days",
            compression="gz",
            filter=self._crash_filter,
        ))

        self._sinks.append(logger.add(
            self.log_dir / "performance.log",
            serialize=True,
            level="DEBUG",
            rotation=self.policy.rotation_size,
            retention=f"{self.policy.retention_days} days",
            compression="gz",
            filter=self._perf_filter,
        ))

        self._sinks.append(logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | <cyan>{module}</cyan> - <level>{message}</level>",
            level="INFO",
            colorize=True,
        ))

    @staticmethod
    def _app_filter(record: dict[str, Any]) -> bool:
        return True

    @staticmethod
    def _crash_filter(record: dict[str, Any]) -> bool:
        return record["level"].no >= 40

    @staticmethod
    def _perf_filter(record: dict[str, Any]) -> bool:
        extra = record.get("extra", {})
        return bool(extra.get("perf")) or record["level"].no >= 40

    @classmethod
    def app(cls, msg: str = "", **kwargs: Any) -> None:
        logger.opt(depth=1).info(msg, **kwargs)

    @classmethod
    def debug(cls, msg: str = "", **kwargs: Any) -> None:
        logger.opt(depth=1).debug(msg, **kwargs)

    @classmethod
    def error(cls, msg: str = "", **kwargs: Any) -> None:
        logger.opt(depth=1).error(msg, **kwargs)

    @classmethod
    def warning(cls, msg: str = "", **kwargs: Any) -> None:
        logger.opt(depth=1).warning(msg, **kwargs)

    @classmethod
    def performance(cls, msg: str = "", **kwargs: Any) -> None:
        logger.opt(depth=1).info(msg, perf=True, **kwargs)

    @classmethod
    def crash(cls, msg: str = "", **kwargs: Any) -> None:
        logger.opt(depth=1).error(msg, crash=True, **kwargs)

    def get_log_files(self) -> dict[str, Path]:
        return {
            "app": self.log_dir / "app.log",
            "crash": self.log_dir / "crash.log",
            "performance": self.log_dir / "performance.log",
        }

    def read_logs(self, log_type: str = "app", lines: int = 100) -> list[dict[str, Any]]:
        log_file = self.log_dir / f"{log_type}.log"
        if not log_file.exists():
            return []
        entries: list[dict[str, Any]] = []
        with open(log_file, encoding="utf-8") as f:
            for line in f.readlines()[-lines:]:
                line = line.strip()
                if line:
                    try:
                        parsed = json.loads(line)
                        record = parsed.get("record", parsed)
                        entries.append(record)
                    except json.JSONDecodeError:
                        entries.append({"raw": line})
        return entries
