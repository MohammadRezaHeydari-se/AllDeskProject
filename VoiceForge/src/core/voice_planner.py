from __future__ import annotations

from dataclasses import dataclass, field

from log_system.logger import LogManager
from models.voice import VoiceProfile


@dataclass
class VoicePlan:
    voice: VoiceProfile
    speed: float = 1.0
    pitch: float = 1.0
    emotion: str = "neutral"
    effects: dict = field(default_factory=dict)


class VoicePlanner:
    def plan(self, voice: VoiceProfile, speed: float = 1.0, emotion: str = "neutral") -> VoicePlan:
        plan = VoicePlan(
            voice=voice,
            speed=speed,
            emotion=emotion,
        )
        LogManager.debug(
            f"Voice plan created: {voice.name}, speed={speed}, emotion={emotion}",
            voice_id=voice.id,
            speed=speed,
            emotion=emotion,
        )
        return plan
