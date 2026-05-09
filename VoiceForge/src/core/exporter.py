from __future__ import annotations

from pathlib import Path
from shutil import copy2

from log_system.logger import LogManager
from models.audio import ExportFormat, GenerationResult


class Exporter:
    def export(self, result: GenerationResult, output_path: Path, fmt: ExportFormat = ExportFormat.WAV) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_path = output_path.with_suffix(f".{fmt.value}")

        if result.output_path.exists():
            copy2(result.output_path, final_path)
            LogManager.app(f"Exported audio to {final_path}", export_format=fmt.value, size=final_path.stat().st_size)
        else:
            LogManager.warning(f"Source file not found: {result.output_path}")

        return final_path
