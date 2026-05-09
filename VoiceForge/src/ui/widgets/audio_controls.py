from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget


class AudioControlsWidget(QGroupBox):
    playRequested = Signal()
    pauseRequested = Signal()
    stopRequested = Signal()
    exportRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Audio Player", parent)
        self._is_playing = False
        self._audio_path: Path | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self._on_play)
        controls.addWidget(self.play_btn)

        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._on_pause)
        controls.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        controls.addWidget(self.stop_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.setEnabled(False)
        self.export_btn.clicked.connect(self.exportRequested.emit)
        controls.addWidget(self.export_btn)

        controls.addStretch()
        layout.addLayout(controls)

        seek_layout = QHBoxLayout()
        self.position_label = QLabel("0:00")
        self.position_label.setStyleSheet("color: #8080a0; font-size: 11px;")
        seek_layout.addWidget(self.position_label)

        self.seek_slider = QSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 100)
        self.seek_slider.setEnabled(False)
        seek_layout.addWidget(self.seek_slider)

        self.duration_label = QLabel("0:00")
        self.duration_label.setStyleSheet("color: #8080a0; font-size: 11px;")
        seek_layout.addWidget(self.duration_label)
        layout.addLayout(seek_layout)

        self.status_label = QLabel("No audio loaded")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #8080a0; font-size: 12px;")
        layout.addWidget(self.status_label)

    def _on_play(self) -> None:
        self._is_playing = True
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.playRequested.emit()

    def _on_pause(self) -> None:
        self._is_playing = False
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pauseRequested.emit()

    def _on_stop(self) -> None:
        self._is_playing = False
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.seek_slider.setValue(0)
        self.stopRequested.emit()

    def load_audio(self, path: Path) -> None:
        self._audio_path = path
        self.play_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.export_btn.setEnabled(True)
        self.seek_slider.setEnabled(True)
        self.seek_slider.setValue(0)
        self.status_label.setText(f"Loaded: {path.name}")

    def reset(self) -> None:
        self._audio_path = None
        self._is_playing = False
        self.play_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.seek_slider.setEnabled(False)
        self.seek_slider.setValue(0)
        self.position_label.setText("0:00")
        self.duration_label.setText("0:00")
        self.status_label.setText("No audio loaded")
