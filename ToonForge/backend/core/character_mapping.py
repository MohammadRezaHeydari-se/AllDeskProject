import re
import os
from pathlib import Path
from typing import Optional


def extract_character_name(filename: str) -> Optional[str]:
    stem = Path(filename).stem
    match = re.match(r'^([a-zA-Z\u0600-\u06FF\s]+?)[_\s]', stem)
    if match:
        return match.group(1).strip().capitalize()
    match = re.match(r'^([a-zA-Z\u0600-\u06FF\s]+)', stem)
    if match:
        return match.group(1).strip().capitalize()
    return None


def auto_map_audio_to_characters(audio_files: list[str], character_images: list[str]) -> dict:
    audio_names = {}
    for af in audio_files:
        name = extract_character_name(os.path.basename(af))
        if name:
            if name not in audio_names:
                audio_names[name] = []
            audio_names[name].append(af)

    char_names = {}
    for ci in character_images:
        name = extract_character_name(os.path.basename(ci))
        if name:
            char_names[name.lower()] = ci

    mapping = {}
    for char_name, audio_list in audio_names.items():
        matched_char = _find_best_match(char_name, list(char_names.keys()))
        if matched_char:
            image_path = char_names[matched_char]
            for audio_path in sorted(audio_list):
                mapping[audio_path] = {
                    "character_name": char_name,
                    "character_image": image_path,
                }
        else:
            for audio_path in audio_list:
                mapping[audio_path] = {
                    "character_name": char_name,
                    "character_image": None,
                }

    return mapping


def _find_best_match(name: str, candidates: list[str]) -> Optional[str]:
    name_lower = name.lower()
    for candidate in candidates:
        if name_lower == candidate.lower():
            return candidate
    for candidate in candidates:
        if name_lower in candidate.lower() or candidate.lower() in name_lower:
            return candidate
    return None


def group_audio_by_character(audio_files: list[str]) -> dict[str, list[str]]:
    groups = {}
    for af in audio_files:
        name = extract_character_name(os.path.basename(af))
        if name:
            if name not in groups:
                groups[name] = []
            groups[name].append(af)
    return groups
