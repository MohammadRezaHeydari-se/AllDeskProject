from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class AudioClip(BaseModel):
    id: str
    filename: str
    filepath: str
    character_id: Optional[str] = None
    duration: float = 0.0
    amplitude_data: Optional[List[float]] = None
    order: int = 0
    subtitle: Optional[str] = None


class Character(BaseModel):
    id: str
    name: str
    image_path: str
    color: str = "#4A90D9"
    is_active: bool = True


class SceneClip(BaseModel):
    audio_id: str
    character_id: str
    order: int
    subtitle: Optional[str] = None


class SceneConfig(BaseModel):
    id: str
    name: str
    background_path: Optional[str] = None
    clips: List[SceneClip] = []
    width: int = 1920
    height: int = 1080
    fps: int = 30
    total_duration: float = 0.0


class ExportFormat(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    BOTH = "both"


class ExportRequest(BaseModel):
    scene_id: str
    format: ExportFormat = ExportFormat.HORIZONTAL
    output_path: Optional[str] = None
    include_subtitles: bool = True
    quality: str = "high"


class Project(BaseModel):
    id: str
    name: str
    characters: List[Character] = []
    audio_clips: List[AudioClip] = []
    scene: Optional[SceneConfig] = None


class MappingOverride(BaseModel):
    audio_id: str
    character_id: str
    order: int
    subtitle: Optional[str] = None
