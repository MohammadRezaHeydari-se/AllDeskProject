from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DebugContext:
    log_snippet: list[dict[str, Any]] = field(default_factory=list)
    stack_trace: str = ""
    system_info: dict = field(default_factory=dict)
    compressed_trace: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "log_snippet": self.log_snippet[-50:],
            "stack_trace": self.stack_trace,
            "system_info": self.system_info,
            "compressed_trace": self.compressed_trace,
        }


class AIDebugAssistant:
    def __init__(self, log_dir: str | Path) -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def prepare_context(self, log_type: str = "crash", lines: int = 100) -> DebugContext:
        ctx = DebugContext()
        ctx.log_snippet = self._load_logs(log_type, lines)
        ctx.system_info = self._get_system_info()
        ctx.stack_trace = self._get_last_trace(ctx.log_snippet)
        ctx.compressed_trace = self._compress_trace(ctx)
        return ctx

    def _load_logs(self, log_type: str, lines: int) -> list[dict[str, Any]]:
        log_file = self.log_dir / f"{log_type}.log"
        if not log_file.exists():
            return []
        entries: list[dict[str, Any]] = []
        with open(log_file, encoding="utf-8") as f:
            for line in f.readlines()[-lines:]:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        entries.append({"raw": line})
        return entries

    def _get_system_info(self) -> dict[str, str]:
        import platform
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
        }

    def _get_last_trace(self, logs: list[dict[str, Any]]) -> str:
        for entry in reversed(logs):
            if exc := entry.get("exception"):
                return exc
        return ""

    @staticmethod
    def _compress_trace(ctx: DebugContext) -> str:
        trace_lines = ctx.stack_trace.splitlines()
        important = [l for l in trace_lines if "Traceback" in l or "Error" in l or "File \"" in l]
        return "\n".join(important[-20:])

    def export_context(self, ctx: DebugContext, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(ctx.to_dict(), f, indent=2, default=str)
        return output_path
