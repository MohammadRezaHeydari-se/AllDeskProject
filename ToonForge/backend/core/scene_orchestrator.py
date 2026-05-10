import json
import os
import uuid
from pathlib import Path
from typing import Optional
from models.schemas import Project, SceneConfig, SceneClip, AudioClip, Character
from core.audio_analysis import get_audio_duration, analyze_phoneme_levels


class SceneOrchestrator:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.audio_dir = self.project_dir / "audio"
        self.characters_dir = self.project_dir / "characters"
        self.background_dir = self.project_dir / "background"
        self.output_dir = self.project_dir / "output"
        self.cache_dir = self.project_dir / "cache"

        for d in [self.audio_dir, self.characters_dir, self.background_dir, self.output_dir, self.cache_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def scan_assets(self, existing_project: Optional[Project] = None) -> Project:
        audio_files = sorted([str(f) for f in self.audio_dir.glob("*.wav")] +
                             [str(f) for f in self.audio_dir.glob("*.mp3")] +
                             [str(f) for f in self.audio_dir.glob("*.ogg")])
        character_images = sorted([str(f) for f in self.characters_dir.glob("*.png")] +
                                  [str(f) for f in self.characters_dir.glob("*.jpg")])
        backgrounds = sorted([str(f) for f in self.background_dir.glob("*.png")] +
                             [str(f) for f in self.background_dir.glob("*.jpg")])

        from core.character_mapping import auto_map_audio_to_characters, extract_character_name
        auto_map = auto_map_audio_to_characters(audio_files, character_images)

        characters: dict[str, Character] = {}
        audio_clips: list[AudioClip] = []
        clips: list[SceneClip] = []

        seen_chars = set()
        for i, af in enumerate(audio_files):
            duration = get_audio_duration(af)
            mapping = auto_map.get(af, {})
            char_name = mapping.get("character_name", f"Character_{i}")
            char_image = mapping.get("character_image")

            if char_name not in seen_chars and char_image:
                char_id = char_name.lower().replace(" ", "_")
                characters[char_id] = Character(
                    id=char_id,
                    name=char_name,
                    image_path=char_image,
                )
                seen_chars.add(char_name)

            char_id = char_name.lower().replace(" ", "_")
            clip_id = f"audio_{i}"
            audio_clips.append(AudioClip(
                id=clip_id,
                filename=os.path.basename(af),
                filepath=af,
                character_id=char_id,
                duration=duration,
                order=i,
            ))

            clips.append(SceneClip(
                audio_id=clip_id,
                character_id=char_id,
                order=i,
            ))

        for ci in character_images:
            name = extract_character_name(os.path.basename(ci))
            if name and name not in seen_chars:
                char_id = name.lower().replace(" ", "_")
                characters[char_id] = Character(
                    id=char_id,
                    name=name,
                    image_path=ci,
                )
                seen_chars.add(name)

        total_duration = sum(c.duration for c in audio_clips)
        bg_path = backgrounds[0] if backgrounds else None

        scene = SceneConfig(
            id="scene_001",
            name="Auto-generated Scene",
            background_path=bg_path,
            clips=sorted(clips, key=lambda c: c.order),
            total_duration=total_duration,
        )

        project_id = existing_project.id if existing_project else str(uuid.uuid4())
        project_name = existing_project.name if existing_project else "New Project"
        return Project(
            id=project_id,
            name=project_name,
            characters=list(characters.values()),
            audio_clips=audio_clips,
            scene=scene,
        )

    def build_scene_manifest(self, project: Project) -> dict:
        manifest = {
            "project_id": project.id,
            "project_name": project.name,
            "width": project.scene.width,
            "height": project.scene.height,
            "fps": project.scene.fps,
            "background": project.scene.background_path,
            "total_duration": project.scene.total_duration,
            "characters": {},
            "timeline": [],
        }

        for char in project.characters:
            manifest["characters"][char.id] = {
                "name": char.name,
                "image": char.image_path,
                "color": char.color,
            }

        current_time = 0.0
        for clip in project.scene.clips:
            audio = next((a for a in project.audio_clips if a.id == clip.audio_id), None)
            if not audio:
                continue

            phoneme_data = analyze_phoneme_levels(audio.filepath, fps=project.scene.fps)
            manifest["timeline"].append({
                "audio_id": clip.audio_id,
                "audio_file": audio.filepath,
                "audio_duration": audio.duration,
                "character_id": clip.character_id,
                "start_time": current_time,
                "end_time": current_time + audio.duration,
                "order": clip.order,
                "subtitle": clip.subtitle or audio.subtitle or "",
                "phoneme_data": phoneme_data,
            })
            current_time += audio.duration

        return manifest

    def update_mapping(self, project: Project, overrides: list) -> Project:
        for override in overrides:
            for clip in project.scene.clips:
                if clip.audio_id == override.audio_id:
                    clip.character_id = override.character_id
                    clip.order = override.order
                    clip.subtitle = override.subtitle
            for audio in project.audio_clips:
                if audio.id == override.audio_id:
                    audio.character_id = override.character_id
                    audio.order = override.order
                    audio.subtitle = override.subtitle

        project.scene.clips.sort(key=lambda c: c.order)
        project.audio_clips.sort(key=lambda a: a.order)

        total = sum(
            a.duration for a in sorted(project.audio_clips, key=lambda x: x.order)
        )
        project.scene.total_duration = total

        return project
