from __future__ import annotations

import asyncio
from pathlib import Path

from PySide6.QtCore import QUrl, Qt, QThread, Signal
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from core.chunk_processor import ChunkProcessor
from core.text_analyzer import TextAnalyzer
from core.tts_engine import TTSEngine
from core.audio_processor import AudioProcessor
from core.exporter import Exporter
from log_system.logger import LogManager
from models.audio import ExportFormat, GenerationResult
from services.config_manager import ConfigManager
from services.gpu_detector import GPUDetector
from ui.styles import STYLESHEET
from ui.widgets.audio_controls import AudioControlsWidget
from ui.widgets.log_center import LogCenterWidget
from ui.widgets.output_settings import OutputSettingsWidget
from ui.widgets.progress_section import ProgressSectionWidget
from ui.widgets.text_editor import TextEditorWidget
from ui.widgets.voice_selector import VoiceSelectorWidget


def resolve_output_path(output_dir: Path, file_name: str, ext: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    counter = 1
    while True:
        name = f"{file_name}_{counter}.{ext}"
        path = output_dir / name
        if not path.exists():
            return path
        counter += 1


class GenerationWorker(QThread):
    progress = Signal(int, int, str)
    finished = Signal(GenerationResult)
    error = Signal(str)

    def __init__(
        self,
        text: str,
        voice_id: str,
        language: str,
        speed: int,
        output_dir: Path,
        file_name: str,
        file_ext: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.text = text
        self.voice_id = voice_id
        self.language = language
        self.speed = speed
        self.output_dir = output_dir
        self.file_name = file_name
        self.file_ext = file_ext
        self._cancelled = False

    def run(self) -> None:
        try:
            analyzer = TextAnalyzer()
            chunk_proc = ChunkProcessor()
            engine = TTSEngine()
            audio_proc = AudioProcessor()

            analysis = analyzer.analyze(self.text, language=self.language)
            if not analysis.is_valid:
                self.error.emit(analysis.errors[0])
                return

            chunks = chunk_proc.process(analysis.sentences, analysis.paragraphs)
            total = len(chunks)
            segments = []
            chunk_dir = self.output_dir / ".chunks"
            chunk_dir.mkdir(parents=True, exist_ok=True)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            for i, chunk in enumerate(chunks):
                if self._cancelled:
                    loop.close()
                    return
                segment = loop.run_until_complete(
                    engine.generate_async(chunk.text, self.voice_id, chunk_dir, i, speed=self.speed)
                )
                segments.append(segment)
                eta = f"~{(total - i) * 3}s"
                self.progress.emit(i + 1, total, eta)

            loop.close()

            if self._cancelled:
                return

            final_path = resolve_output_path(self.output_dir, self.file_name, self.file_ext)
            merged = audio_proc.merge_segments(segments, final_path)
            total_seconds = sum(s.duration_seconds for s in segments)

            result = GenerationResult(
                output_path=merged,
                segments=segments,
                total_duration_seconds=total_seconds,
                chunk_count=total,
                voice_id=self.voice_id,
                text_length=len(self.text),
            )

            self.finished.emit(result)
            LogManager.app(
                f"Generation complete: {total} chunks, {total_seconds:.1f}s audio",
                chunks=total,
                duration=total_seconds,
            )
        except Exception as exc:
            LogManager.error(f"Generation failed: {exc}")
            self.error.emit(str(exc))

    def cancel(self) -> None:
        self._cancelled = True


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.config = ConfigManager.get_instance()
        self._gpu_info = GPUDetector.detect()
        self._worker: GenerationWorker | None = None

        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)

        self._setup_window()
        self._setup_ui()
        self._apply_config()
        self._log_startup()

    def _setup_window(self) -> None:
        self.setWindowTitle("VoiceForge")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(STYLESHEET)

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)

        title_label = QLabel("VoiceForge")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        subtitle = QLabel(f"AI Voice Generation  |  {self._gpu_info.gpu_type.value.upper()}  |  v1.0.0")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #8080a0; font-size: 12px; padding-bottom: 8px;")
        main_layout.addWidget(subtitle)

        self._output_path_label = QLabel("")
        self._output_path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._output_path_label.setStyleSheet("color: #e94560; font-size: 11px;")
        main_layout.addWidget(self._output_path_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 8, 0)

        self.voice_selector = VoiceSelectorWidget()
        left_layout.addWidget(self.voice_selector)

        self.text_editor = TextEditorWidget()
        left_layout.addWidget(self.text_editor, 1)

        self.generate_btn = QPushButton("Generate Speech")
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.clicked.connect(self._start_generation)
        left_layout.addWidget(self.generate_btn)

        splitter.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(8, 0, 0, 0)

        self.audio_controls = AudioControlsWidget()
        self.audio_controls.playRequested.connect(self._play_audio)
        self.audio_controls.pauseRequested.connect(self._player.pause)
        self.audio_controls.stopRequested.connect(self._stop_audio)
        self.audio_controls.exportRequested.connect(self._export_audio)
        right_layout.addWidget(self.audio_controls)

        self.progress_section = ProgressSectionWidget()
        self.progress_section.cancelled.connect(self._cancel_generation)
        right_layout.addWidget(self.progress_section)

        self.output_settings = OutputSettingsWidget()
        right_layout.addWidget(self.output_settings)

        right_layout.addStretch()

        splitter.addWidget(right_panel)
        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter, 1)

        log_dir = Path(__file__).parent.parent / "logs"
        self.log_center = LogCenterWidget(log_dir)
        main_layout.addWidget(self.log_center)

        self._player.positionChanged.connect(self._update_seek)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status)

    def _apply_config(self) -> None:
        if default_dir := self.config.get("default_output_dir"):
            self.output_settings.dir_input.setText(default_dir)
        if default_voice := self.config.get("default_voice"):
            idx = self.voice_selector.voice_combo.findData(default_voice)
            if idx >= 0:
                self.voice_selector.voice_combo.setCurrentIndex(idx)
        if default_lang := self.config.get("default_language"):
            idx = self.voice_selector.lang_combo.findData(default_lang)
            if idx >= 0:
                self.voice_selector.lang_combo.setCurrentIndex(idx)
        if fmt := self.config.get("export_format"):
            idx = self.output_settings.format_combo.findText(fmt)
            if idx >= 0:
                self.output_settings.format_combo.setCurrentIndex(idx)
        if default_speed := self.config.get("default_speed"):
            self.output_settings.set_speed(default_speed)

        self.voice_selector.languageChanged.connect(self._on_language_changed)

    def _log_startup(self) -> None:
        LogManager.app("VoiceForge started",
                       gpu=self._gpu_info.gpu_type.value,
                       gpu_name=self._gpu_info.name,
                       python_version=__import__("sys").version)

    def _start_generation(self) -> None:
        text = self.text_editor.get_text()
        if not text.strip():
            QMessageBox.warning(self, "No Text", "Please enter some text to generate speech.")
            return

        voice_id = self.voice_selector.current_voice_id()
        language = self.voice_selector.current_language()
        speed = self.output_settings.get_speed()
        output_dir = self.output_settings.get_output_path()
        file_name = self.output_settings.get_file_name()
        file_ext = self.output_settings.get_format()

        preview_path = resolve_output_path(output_dir, file_name, file_ext)
        self._output_path_label.setText(f"Will save to: {preview_path}")

        self.generate_btn.setEnabled(False)
        self.progress_section.start()
        self.audio_controls.reset()

        self._worker = GenerationWorker(text, voice_id, language, speed, output_dir, file_name, file_ext, self)
        self._worker.progress.connect(self.progress_section.update_progress)
        self._worker.finished.connect(self._on_generation_finished)
        self._worker.error.connect(self._on_generation_error)
        self._worker.start()

    def _on_generation_finished(self, result: GenerationResult) -> None:
        self.generate_btn.setEnabled(True)
        self.progress_section.complete()
        self._current_result = result
        self.audio_controls.load_audio(result.output_path)

        self._output_path_label.setText(f"Saved to: {result.output_path}")

        self.config.add_recent_output(str(result.output_path))
        LogManager.app(f"Audio generated: {result.output_path}",
                       chunks=result.chunk_count,
                       duration=result.total_duration_seconds)

    def _on_generation_error(self, message: str) -> None:
        self.generate_btn.setEnabled(True)
        self.progress_section.error(message)
        QMessageBox.critical(self, "Generation Failed", message)

    def _on_language_changed(self, language: str) -> None:
        self.config.set("default_language", language)
        LogManager.app(f"Language changed to {language}")

    def _cancel_generation(self) -> None:
        if self._worker:
            self._worker.cancel()
        self.generate_btn.setEnabled(True)
        self.progress_section.reset()
        LogManager.app("Generation cancelled by user")

    def _play_audio(self) -> None:
        if not hasattr(self, "_current_result"):
            return
        path = self._current_result.output_path
        if not path.exists():
            QMessageBox.warning(self, "File Not Found", f"Audio file not found:\n{path}")
            return
        self._player.setSource(QUrl.fromLocalFile(str(path)))
        self._player.play()

    def _stop_audio(self) -> None:
        self._player.stop()
        self.audio_controls.seek_slider.setValue(0)
        self.audio_controls.position_label.setText("0:00")
        self.audio_controls.play_btn.setEnabled(True)
        self.audio_controls.pause_btn.setEnabled(False)
        self.audio_controls.stop_btn.setEnabled(False)

    def _export_audio(self) -> None:
        if not hasattr(self, "_current_result"):
            return
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Audio",
            str(self._current_result.output_path),
            "Audio Files (*.wav *.mp3 *.flac *.ogg);;All Files (*)",
        )
        if path:
            from shutil import copy2
            copy2(self._current_result.output_path, path)
            LogManager.app(f"Exported audio to {path}")
            QMessageBox.information(self, "Exported", f"Audio saved to:\n{path}")

    def _update_seek(self, position: int) -> None:
        duration = self._player.duration()
        if duration > 0:
            self.audio_controls.seek_slider.setValue(int(position / duration * 100))
            seconds = position // 1000
            self.audio_controls.position_label.setText(f"{seconds // 60}:{seconds % 60:02d}")

    def _on_duration_changed(self, duration: int) -> None:
        if duration > 0:
            seconds = duration // 1000
            self.audio_controls.duration_label.setText(f"{seconds // 60}:{seconds % 60:02d}")

    def _on_media_status(self, status: QMediaPlayer.MediaStatus) -> None:
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._stop_audio()

    def closeEvent(self, event) -> None:
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)
        self._player.stop()
        self.config.save()
        LogManager.app("VoiceForge shutting down")
        super().closeEvent(event)
