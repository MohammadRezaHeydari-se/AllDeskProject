import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Optional

from models.schemas import Project, Character, AudioClip, SceneConfig, SceneClip


class ProjectService:
    def __init__(self, projects_root: str):
        self.projects_root = Path(projects_root)
        self.projects_root.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str) -> Project:
        project = Project(
            id=str(uuid.uuid4()),
            name=name,
        )
        self._save_project(project)
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        path = self._project_path(project_id)
        if not path.exists():
            return None
        with open(path / "project.json", "r") as f:
            return Project.model_validate_json(f.read())

    def list_projects(self) -> list[Project]:
        projects = []
        for d in self.projects_root.iterdir():
            if d.is_dir() and (d / "project.json").exists():
                with open(d / "project.json", "r") as f:
                    projects.append(Project.model_validate_json(f.read()))
        return projects

    def save_project(self, project: Project):
        self._save_project(project)

    def _save_project(self, project: Project):
        path = self._project_path(project.id)
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "project.json", "w") as f:
            f.write(project.model_dump_json(indent=2))

    def _project_path(self, project_id: str) -> Path:
        return self.projects_root / project_id

    def import_audio(self, project_id: str, source_paths: list[str],
                     original_filenames: Optional[list[str]] = None) -> list[AudioClip]:
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        audio_dir = self._project_path(project_id) / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        from core.character_mapping import extract_character_name
        from core.audio_analysis import get_audio_duration
        new_clips = []
        for i, src in enumerate(source_paths):
            orig_name = original_filenames[i] if original_filenames else os.path.basename(src)
            dest = audio_dir / orig_name
            shutil.copy2(src, dest)
            char_name = extract_character_name(orig_name)
            duration = get_audio_duration(str(dest))
            clip = AudioClip(
                id=f"audio_{len(project.audio_clips) + i}",
                filename=orig_name,
                filepath=str(dest),
                character_id=char_name.lower().replace(" ", "_") if char_name else None,
                duration=duration,
                order=len(project.audio_clips) + i,
            )
            new_clips.append(clip)
            project.audio_clips.append(clip)

        self._save_project(project)
        return new_clips

    def import_characters(self, project_id: str, source_paths: list[str],
                          original_filenames: Optional[list[str]] = None) -> list[Character]:
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        chars_dir = self._project_path(project_id) / "characters"
        chars_dir.mkdir(parents=True, exist_ok=True)

        from core.character_mapping import extract_character_name
        new_chars = []
        for i, src in enumerate(source_paths):
            orig_name = original_filenames[i] if original_filenames else os.path.basename(src)
            dest = chars_dir / orig_name
            shutil.copy2(src, dest)
            name = extract_character_name(orig_name) or f"Character_{len(project.characters)}"
            char = Character(
                id=name.lower().replace(" ", "_"),
                name=name,
                image_path=str(dest),
            )
            new_chars.append(char)
            project.characters.append(char)

        self._save_project(project)
        return new_chars

    def import_background(self, project_id: str, source_path: str,
                          original_filename: Optional[str] = None) -> str:
        project = self.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")

        bg_dir = self._project_path(project_id) / "background"
        bg_dir.mkdir(parents=True, exist_ok=True)

        orig_name = original_filename or os.path.basename(source_path)
        dest = bg_dir / orig_name
        shutil.copy2(source_path, dest)

        if not project.scene:
            project.scene = SceneConfig(id="scene_001", name="Main Scene")
        project.scene.background_path = str(dest)

        self._save_project(project)
        return str(dest)
