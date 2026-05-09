from __future__ import annotations

from pathlib import Path
from typing import Sequence

from pydub import AudioSegment as PydubSegment

from log_system.logger import LogManager
from models.audio import AudioSegment, ExportFormat


class AudioProcessor:
    def merge_segments(self, segments: Sequence[AudioSegment], output_path: Path) -> Path:
        if not segments:
            raise ValueError("No audio segments to merge")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        LogManager.app(f"Merging {len(segments)} audio segments to {output_path}", segment_count=len(segments))

        combined = PydubSegment.empty()
        for seg in segments:
            if seg.path.exists():
                chunk = PydubSegment.from_file(str(seg.path))
                combined += chunk
            else:
                LogManager.warning(f"Segment not found: {seg.path}")

        combined.export(str(output_path), format="wav")
        combined_length = combined.duration_seconds

        LogManager.debug(f"Merged audio: {combined_length:.1f}s, {output_path}")
        return output_path

    def convert_format(self, source: Path, target_format: ExportFormat, output_dir: Path) -> Path:
        output_path = output_dir / f"{source.stem}.{target_format.value}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        LogManager.debug(f"Converting {source} to {target_format.value}")
        audio = PydubSegment.from_file(str(source))
        audio.export(str(output_path), format=target_format.value)
        return output_path

    def get_duration(self, audio_path: Path) -> float:
        try:
            seg = PydubSegment.from_file(str(audio_path))
            return seg.duration_seconds
        except Exception:
            return 0.0

    def normalize_audio(self, audio_path: Path) -> Path:
        LogManager.debug(f"Normalizing audio: {audio_path}")
        audio = PydubSegment.from_file(str(audio_path))
        normalized = audio.apply_gain(-audio.dBFS)
        normalized.export(str(audio_path), format=audio_path.suffix[1:])
        return audio_path
