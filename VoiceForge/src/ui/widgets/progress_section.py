from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget


class ProgressSectionWidget(QWidget):
    cancelled = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self.reset()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Generation Progress")
        title.setObjectName("sectionLabel")
        layout.addWidget(title)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        info_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #8080a0;")
        info_layout.addWidget(self.status_label)

        info_layout.addStretch()

        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet("color: #8080a0; font-size: 12px;")
        info_layout.addWidget(self.eta_label)
        layout.addLayout(info_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancelled.emit)
        self.cancel_btn.setVisible(False)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def start(self, total_steps: int = 100) -> None:
        self.progress_bar.setRange(0, total_steps)
        self.progress_bar.setValue(0)
        self.status_label.setText("Generating...")
        self.cancel_btn.setVisible(True)
        self.eta_label.setText("Estimating...")

    def update_progress(self, current: int, total: int, eta: str = "") -> None:
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(f"Processing chunk {current}/{total}")
        if eta:
            self.eta_label.setText(f"ETA: {eta}")

    def complete(self) -> None:
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.status_label.setText("Generation complete!")
        self.eta_label.setText("")
        self.cancel_btn.setVisible(False)

    def error(self, message: str) -> None:
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: #e94560;")
        self.cancel_btn.setVisible(False)

    def reset(self) -> None:
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.status_label.setStyleSheet("color: #8080a0;")
        self.eta_label.setText("")
        self.cancel_btn.setVisible(False)
