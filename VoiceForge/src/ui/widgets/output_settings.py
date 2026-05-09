from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSlider, QVBoxLayout, QWidget,
)


class OutputSettingsWidget(QGroupBox):
    outputDirChanged = Signal(str)
    formatChanged = Signal(str)
    speedChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Output Settings", parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Output Folder:"))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText(str(Path.home() / "VoiceForge_Output"))
        self.dir_input.textChanged.connect(lambda v: self.outputDirChanged.emit(v))
        dir_layout.addWidget(self.dir_input, 1)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._browse_dir)
        dir_layout.addWidget(self.browse_btn)
        layout.addLayout(dir_layout)

        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("File Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("voiceforge_output")
        name_layout.addWidget(self.name_input, 1)
        layout.addLayout(name_layout)

        fmt_layout = QHBoxLayout()
        fmt_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["wav", "mp3", "flac", "ogg"])
        self.format_combo.currentTextChanged.connect(self.formatChanged.emit)
        fmt_layout.addWidget(self.format_combo)
        fmt_layout.addStretch()

        self.default_btn = QPushButton("Set as Default")
        self.default_btn.clicked.connect(self._set_default)
        fmt_layout.addWidget(self.default_btn)
        layout.addLayout(fmt_layout)

        speed_layout = QVBoxLayout()
        speed_title = QHBoxLayout()
        speed_title.addWidget(QLabel("Speed:"))
        self.speed_label = QLabel("100%")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.speed_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        speed_title.addWidget(self.speed_label)
        speed_layout.addLayout(speed_title)

        slider_row = QHBoxLayout()
        slider_row.addWidget(QLabel("50%"))
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(50, 200)
        self.speed_slider.setValue(100)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(10)
        self.speed_slider.valueChanged.connect(self._on_speed_changed)
        slider_row.addWidget(self.speed_slider, 1)
        slider_row.addWidget(QLabel("200%"))
        speed_layout.addLayout(slider_row)

        layout.addLayout(speed_layout)

    def _on_speed_changed(self, value: int) -> None:
        self.speed_label.setText(f"{value}%")
        self.speedChanged.emit(value)

    def _browse_dir(self) -> None:
        from PySide6.QtWidgets import QFileDialog
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.dir_input.setText(directory)

    def _set_default(self) -> None:
        from services.config_manager import ConfigManager
        cm = ConfigManager.get_instance()
        cm.set("default_output_dir", self.dir_input.text())
        cm.set("export_format", self.format_combo.currentText())
        cm.set("default_speed", self.speed_slider.value())

    def get_output_path(self) -> Path:
        path = self.dir_input.text().strip()
        return Path(path) if path else Path.home() / "VoiceForge_Output"

    def get_file_name(self) -> str:
        name = self.name_input.text().strip()
        return name if name else "voiceforge_output"

    def get_format(self) -> str:
        return self.format_combo.currentText()

    def get_speed(self) -> int:
        return self.speed_slider.value()

    def set_speed(self, value: int) -> None:
        self.speed_slider.setValue(value)
