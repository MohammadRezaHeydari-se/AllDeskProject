import os
import re
from typing import Optional


class SubtitleGenerator:
    def __init__(self, srt_path: Optional[str] = None):
        self.srt_path = srt_path
        self.subtitles: list[dict] = []
        if srt_path and os.path.exists(srt_path):
            self._parse_srt(srt_path)

    def _parse_srt(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        blocks = re.split(r'\n\s*\n', content.strip())
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                time_line = lines[1]
                text = '\n'.join(lines[2:])
                time_match = re.match(
                    r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)',
                    time_line
                )
                if time_match:
                    start = (
                        int(time_match.group(1)) * 3600
                        + int(time_match.group(2)) * 60
                        + int(time_match.group(3))
                        + int(time_match.group(4)) / 1000
                    )
                    end = (
                        int(time_match.group(5)) * 3600
                        + int(time_match.group(6)) * 60
                        + int(time_match.group(7))
                        + int(time_match.group(8)) / 1000
                    )
                    self.subtitles.append({
                        "start": start,
                        "end": end,
                        "text": text.strip(),
                    })

    def get_subtitle_at(self, time: float) -> Optional[str]:
        for sub in self.subtitles:
            if sub["start"] <= time <= sub["end"]:
                return sub["text"]
        return None

    @staticmethod
    def generate_empty_subtitle(audio_path: str, duration: float) -> list[dict]:
        filename = os.path.basename(audio_path)
        name = os.path.splitext(filename)[0]
        return [{"start": 0, "end": duration, "text": name}]


def extract_text_from_filename(filepath: str) -> Optional[str]:
    stem = os.path.splitext(os.path.basename(filepath))[0]
    parts = stem.split('_', 1)
    if len(parts) > 1:
        return parts[1].replace('_', ' ').replace('-', ' ').strip()
    return None
