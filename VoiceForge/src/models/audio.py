from __future__ import annotations

import enum
from dataclasses import dataclass, field
from pathlib import Path


class ExportFormat(enum.Enum):
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"


@dataclass
class AudioSegment:
    path: Path
    duration_seconds: float
    format: str = "wav"
    sample_rate: int = 24000
    metadata: dict = field(default_factory=dict)


@dataclass
class GenerationResult:
    output_path: Path
    segments: list[AudioSegment] = field(default_factory=list)
    total_duration_seconds: float = 0.0
    chunk_count: int = 0
    voice_id: str = ""
    text_length: int = 0
    generation_time_seconds: float = 0.0
    metadata: dict = field(default_factory=dict)
