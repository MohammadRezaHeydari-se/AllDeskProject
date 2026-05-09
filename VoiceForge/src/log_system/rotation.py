from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RotationPolicy:
    daily: bool = True
    max_size_mb: int = 50
    retention_days: int = 14
    archive_cleanup: bool = True
    max_files: int = 30

    @property
    def rotation_size(self) -> str:
        return f"{self.max_size_mb} MB"

    @property
    def rotation_time(self) -> str:
        return "00:00"
