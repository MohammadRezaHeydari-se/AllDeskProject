from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QWidget

MAX_CHARS = 5000


class TextEditorWidget(QWidget):
    textChanged = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        title = QLabel("Text Input")
        title.setObjectName("sectionLabel")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.char_count_label = QLabel("0 / 5000")
        self.char_count_label.setStyleSheet("color: #8080a0; font-size: 12px;")
        header_layout.addWidget(self.char_count_label)
        layout.addLayout(header_layout)

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("Enter up to 5000 characters of text to convert to speech...")
        self.text_edit.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.text_edit, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.text_edit.clear)
        button_layout.addWidget(self.clear_btn)
        layout.addLayout(button_layout)

    def _on_text_changed(self) -> None:
        text = self.text_edit.toPlainText()
        length = len(text)
        if length > MAX_CHARS:
            cursor = self.text_edit.textCursor()
            self.text_edit.setPlainText(text[:MAX_CHARS])
            self.text_edit.setTextCursor(cursor)

        current = min(length, MAX_CHARS)
        self.char_count_label.setText(f"{current} / {MAX_CHARS}")
        if current >= MAX_CHARS:
            self.char_count_label.setStyleSheet("color: #e94560; font-size: 12px;")
        else:
            self.char_count_label.setStyleSheet("color: #8080a0; font-size: 12px;")

        self.textChanged.emit(self.text_edit.toPlainText())

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    def set_text(self, text: str) -> None:
        self.text_edit.setPlainText(text)
