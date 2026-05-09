from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Protocol

from edge_tts import Communicate
from gtts import gTTS

from log_system.logger import LogManager
from models.audio import AudioSegment
from models.voice import VOICE_MAP, DEFAULT_VOICE


class TTSBackend(Protocol):
    async def generate(self, text: str, voice_id: str, output_path: Path, speed: int = 100) -> Path:
        ...


def _speed_to_rate(speed: int) -> str:
    return f"{speed - 100:+d}%"


class EdgeTTSBackend:
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]

    async def generate(self, text: str, voice_id: str, output_path: Path, speed: int = 100) -> Path:
        voice = VOICE_MAP.get(voice_id)
        if not voice:
            voice = VOICE_MAP[DEFAULT_VOICE]

        rate = _speed_to_rate(speed)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        last_exc = None
        for attempt in range(self.MAX_RETRIES):
            try:
                communicate = Communicate(
                    text,
                    voice=voice.edge_voice,
                    rate=rate,
                    pitch=voice.edge_pitch,
                )
                await communicate.save(str(output_path))
                LogManager.debug(
                    f"edge-tts generated: voice={voice.edge_voice}, "
                    f"rate={rate}, pitch={voice.edge_pitch}, "
                    f"text_len={len(text)}, output={output_path}"
                )
                return output_path
            except Exception as exc:
                last_exc = exc
                LogManager.warning(
                    f"edge-tts attempt {attempt + 1}/{self.MAX_RETRIES} failed: {exc}",
                    voice_id=voice_id,
                )
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(self.RETRY_DELAYS[attempt])
        raise last_exc  # type: ignore


class GoogleTTSBackend(TTSBackend):
    def __init__(self) -> None:
        try:
            from gtts.lang import tts_langs
            self._supported = set(tts_langs().keys())
        except Exception:
            self._supported = {"en"}

    async def generate(self, text: str, voice_id: str, output_path: Path, speed: int = 100) -> Path:
        voice = VOICE_MAP.get(voice_id)
        if not voice:
            voice = VOICE_MAP[DEFAULT_VOICE]

        lang = voice.language
        if lang not in self._supported:
            raise RuntimeError(
                f"gTTS does not support language '{lang}' for voice '{voice_id}'. "
                f"Supported: {sorted(self._supported)}"
            )
        LogManager.debug(f"gTTS fallback generating: voice={voice_id}, lang={lang}, text_len={len(text)}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tts = gTTS(text, lang=lang)
        tts.save(str(output_path))
        LogManager.debug(f"gTTS fallback saved: output={output_path}")
        return output_path


class TTSEngine:
    def __init__(self, backend: TTSBackend | None = None) -> None:
        self.backend = backend or EdgeTTSBackend()
        self._fallback: TTSBackend | None = GoogleTTSBackend()

    async def generate_async(
        self, text: str, voice_id: str, output_dir: Path,
        chunk_index: int = 0, speed: int = 100,
    ) -> AudioSegment:
        voice = VOICE_MAP.get(voice_id)
        if not voice:
            raise ValueError(f"Unknown voice: {voice_id}")

        output_path = output_dir / f"chunk_{chunk_index:04d}.mp3"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        LogManager.app(
            f"Generating audio for chunk {chunk_index} with voice {voice.name} ({voice.age}, {voice.language})",
            voice_id=voice_id,
            chunk_index=chunk_index,
            text_length=len(text),
        )

        try:
            await self.backend.generate(text, voice_id, output_path, speed=speed)
        except Exception as exc:
            LogManager.error(f"Primary backend failed: {exc}", voice_id=voice_id, chunk_index=chunk_index)
            if self._fallback:
                LogManager.app("Falling back to Google TTS backend")
                try:
                    await self._fallback.generate(text, voice_id, output_path, speed=speed)
                except Exception as fallback_exc:
                    LogManager.error(f"Fallback also failed: {fallback_exc}")
                    raise exc from fallback_exc
            else:
                raise

        duration = self._get_duration(output_path)
        return AudioSegment(
            path=output_path,
            duration_seconds=duration,
            metadata={"voice_id": voice_id, "chunk_index": chunk_index, "text": text[:100]},
        )

    def generate(
        self, text: str, voice_id: str, output_dir: Path,
        chunk_index: int = 0, speed: int = 100,
    ) -> AudioSegment:
        return asyncio.run(self.generate_async(text, voice_id, output_dir, chunk_index, speed=speed))

    @staticmethod
    def _get_duration(audio_path: Path) -> float:
        try:
            from pydub import AudioSegment as PydubSegment
            seg = PydubSegment.from_file(str(audio_path))
            return seg.duration_seconds
        except Exception:
            return 0.0
