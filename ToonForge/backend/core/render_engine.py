import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from models.schemas import ExportFormat


class RenderEngine:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self.progress_callback = None

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def render_manifest(self, manifest: dict, output_path: str,
                        fmt: ExportFormat = ExportFormat.HORIZONTAL,
                        include_subtitles: bool = True,
                        quality: str = "high") -> str:
        manifest_path = self._save_manifest(manifest)

        if fmt == ExportFormat.BOTH:
            hor_path = output_path.replace(".mp4", "_horizontal.mp4")
            ver_path = output_path.replace(".mp4", "_vertical.mp4")
            self._render_single(manifest_path, hor_path, 1920, 1080, include_subtitles, quality)
            self._render_single(manifest_path, ver_path, 1080, 1920, include_subtitles, quality)
            return f"{hor_path}\n{ver_path}"
        elif fmt == ExportFormat.VERTICAL:
            return self._render_single(manifest_path, output_path, 1080, 1920, include_subtitles, quality)
        else:
            return self._render_single(manifest_path, output_path, 1920, 1080, include_subtitles, quality)

    def _save_manifest(self, manifest: dict) -> str:
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(manifest, tmp, ensure_ascii=False, indent=2)
        tmp.flush()
        return tmp.name

    def _render_single(self, manifest_path: str, output_path: str,
                       width: int, height: int,
                       include_subtitles: bool, quality: str) -> str:
        manifest = json.load(open(manifest_path, "r"))

        if quality == "high":
            crf = "18"
            preset = "medium"
        elif quality == "medium":
            crf = "23"
            preset = "fast"
        else:
            crf = "28"
            preset = "veryfast"

        scene_dir = tempfile.mkdtemp()
        frames_dir = Path(scene_dir) / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        try:
            self._generate_frames(manifest, str(frames_dir), width, height, include_subtitles)
            video_path = self._compile_video(str(frames_dir), output_path, manifest["fps"], crf, preset, width, height)
            audio_path = self._merge_audio(manifest, scene_dir)
            if audio_path:
                self._mux_audio_video(video_path, audio_path, output_path)
            else:
                import shutil
                shutil.move(video_path, output_path)
            return output_path
        finally:
            import shutil
            shutil.rmtree(scene_dir, ignore_errors=True)
            os.unlink(manifest_path)

    def _generate_frames(self, manifest: dict, frames_dir: str,
                         width: int, height: int,
                         include_subtitles: bool):
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont

        fps = manifest["fps"]
        total_frames = int(manifest["total_duration"] * fps)

        bg_path = manifest.get("background")
        bg_image = None
        if bg_path and os.path.exists(bg_path):
            bg_image = Image.open(bg_path).convert("RGBA")
            bg_image = bg_image.resize((width, height), Image.LANCZOS)

        timeline = manifest["timeline"]
        characters = manifest["characters"]

        char_images = {}
        for cid, cdata in characters.items():
            img_path = cdata.get("image")
            if img_path and os.path.exists(img_path):
                img = Image.open(img_path).convert("RGBA")
                char_images[cid] = img

        char_state = {}
        for frame_idx in range(total_frames):
            if self.progress_callback and total_frames > 0:
                pct = int((frame_idx / total_frames) * 100)
                self.progress_callback(pct)

            current_time = frame_idx / fps
            canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

            if bg_image:
                canvas.paste(bg_image, (0, 0), bg_image if bg_image.mode == "RGBA" else None)
            else:
                draw = ImageDraw.Draw(canvas)
                draw.rectangle([(0, 0), (width, height)], fill=(30, 40, 60))

            active_clip = None
            for clip in timeline:
                if clip["start_time"] <= current_time < clip["end_time"]:
                    active_clip = clip
                    break

            active_char_id = active_clip["character_id"] if active_clip else None

            for cid, cdata in characters.items():
                if cid not in char_images:
                    continue

                img = char_images[cid]
                is_active = (cid == active_char_id)

                if cid not in char_state:
                    char_state[cid] = {
                        "blink_timer": np.random.randint(30, 90),
                        "is_blinking": False,
                        "blink_frame": 0,
                        "head_offset": 0.0,
                        "mouth_open": 0.0,
                    }

                state = char_state[cid]
                state["blink_timer"] -= 1

                if state["blink_timer"] <= 0 and not state["is_blinking"]:
                    state["is_blinking"] = True
                    state["blink_frame"] = 0

                if state["is_blinking"]:
                    state["blink_frame"] += 1
                    if state["blink_frame"] > 4:
                        state["is_blinking"] = False
                        state["blink_timer"] = np.random.randint(60, 180)

                if is_active and active_clip:
                    local_frame = max(0, frame_idx - int(active_clip["start_time"] * fps))
                    phoneme_idx = min(local_frame, len(active_clip["phoneme_data"]) - 1)
                    if phoneme_idx >= 0:
                        phoneme = active_clip["phoneme_data"][phoneme_idx]
                        state["mouth_open"] = phoneme["mouth_open"]
                        state["head_offset"] = np.sin(current_time * 3.0) * 0.02
                else:
                    state["mouth_open"] = 0.0
                    state["head_offset"] = np.sin(current_time * 1.5 + hash(cid) % 10) * 0.01

                char_width = width // 4
                aspect = img.width / img.height
                char_height = int(char_width / aspect) if aspect else height // 2

                if char_height > height * 0.8:
                    char_height = int(height * 0.8)
                    char_width = int(char_height * aspect)

                resized = img.resize((char_width, char_height), Image.BILINEAR)

                if state["is_blinking"]:
                    blink_progress = state["blink_frame"] / 4.0
                    blink_scale = 1.0 - (blink_progress * 0.3)
                    new_h = int(char_height * blink_scale)
                    if new_h > 0:
                        resized = img.resize((char_width, new_h), Image.BILINEAR)
                    else:
                        resized = img.resize((char_width, 1), Image.BILINEAR)

                if is_active and state["mouth_open"] > 0.1:
                    mouth_scale = 1.0 + state["mouth_open"] * 0.05
                    new_h = int(char_height * mouth_scale)
                    if new_h > 0 and new_h != char_height:
                        resized = img.resize((char_width, new_h), Image.BILINEAR)

                offset_x = int(state["head_offset"] * width)
                is_left = (list(characters.keys()).index(cid) % 2 == 0)

                if is_left:
                    x = int(width * 0.15) + offset_x - char_width // 2
                else:
                    x = int(width * 0.85) + offset_x - char_width // 2

                y = height - char_height - int(height * 0.05)

                canvas.paste(resized, (x, y), resized)

                if include_subtitles and is_active and active_clip and active_clip.get("subtitle"):
                    draw = ImageDraw.Draw(canvas)
                    subtitle = active_clip["subtitle"]
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
                    except (IOError, OSError):
                        font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), subtitle, font=font)
                    tw = bbox[2] - bbox[0]
                    th = bbox[3] - bbox[1]
                    sx = x + char_width // 2 - tw // 2
                    sy = y + char_height + 10
                    draw.text((sx + 2, sy + 2), subtitle, fill=(0, 0, 0, 180), font=font)
                    draw.text((sx, sy), subtitle, fill=(255, 255, 255, 255), font=font)

            frame_path = os.path.join(frames_dir, f"frame_{frame_idx:06d}.jpg")
            canvas.convert("RGB").save(frame_path, "JPEG", quality=85)

    def _compile_video(self, frames_dir: str, output_path: str,
                       fps: int, crf: str, preset: str,
                       width: int, height: int) -> str:
        temp_video = output_path.replace(".mp4", "_temp.mp4")
        cmd = [
            self.ffmpeg_path, "-y",
            "-framerate", str(fps),
            "-i", os.path.join(frames_dir, "frame_%06d.jpg"),
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", crf,
            "-pix_fmt", "yuv420p",
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-an",
            temp_video,
        ]
        import glob
        existing = list(glob.glob(os.path.join(frames_dir, "*.jpg")))
        if not existing:
            raise RuntimeError(f"No frames generated in {frames_dir}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed (exit {result.returncode}): {result.stderr[:500]}")
        return temp_video

    def _merge_audio(self, manifest: dict, work_dir: str) -> Optional[str]:
        timeline = manifest["timeline"]
        if not timeline:
            return None

        audio_list_path = os.path.join(work_dir, "audio_list.txt")
        with open(audio_list_path, "w") as f:
            for clip in timeline:
                audio_file = clip["audio_file"]
                if os.path.exists(audio_file):
                    start = clip["start_time"]
                    f.write(f"file '{audio_file}'\n")
                    f.write(f"inpoint 0\n")

        merged = os.path.join(work_dir, "merged_audio.wav")
        cmd = [
            self.ffmpeg_path, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", audio_list_path,
            "-c", "pcm_s16le",
            merged,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return merged
        except subprocess.CalledProcessError:
            return None

    def _mux_audio_video(self, video_path: str, audio_path: str, output_path: str):
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        if os.path.exists(video_path) and video_path != output_path:
            os.unlink(video_path)
