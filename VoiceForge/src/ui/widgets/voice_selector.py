from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from models.voice import VOICE_CATALOG, VoiceGender, get_languages, DEFAULT_VOICE


LANG_LABELS: dict[str, str] = {
    "en": "English",
    "sv": "Swedish",
    "fa": "Persian (Farsi)",
}


class VoiceSelectorWidget(QGroupBox):
    voiceChanged = Signal(str)
    languageChanged = Signal(str)
    previewRequested = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Voice Selection", parent)
        self._current_language = "en"
        self._setup_ui()
        self._populate_languages()
        self._apply_filter()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.currentIndexChanged.connect(self._on_language_changed)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)

        gender_layout = QHBoxLayout()
        gender_layout.addWidget(QLabel("Gender:"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["All", "Male", "Female"])
        self.gender_combo.currentTextChanged.connect(self._apply_filter)
        gender_layout.addWidget(self.gender_combo)
        gender_layout.addStretch()
        layout.addLayout(gender_layout)

        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.currentIndexChanged.connect(self._on_voice_changed)
        voice_layout.addWidget(self.voice_combo, 1)
        layout.addLayout(voice_layout)

        preview_layout = QHBoxLayout()
        preview_layout.addStretch()
        self.preview_btn = QPushButton("Preview Voice")
        self.preview_btn.clicked.connect(self._on_preview)
        preview_layout.addWidget(self.preview_btn)
        layout.addLayout(preview_layout)

        self.desc_label = QLabel()
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.desc_label)

    def _populate_languages(self) -> None:
        self.lang_combo.clear()
        langs = sorted(get_languages())
        for code in langs:
            label = LANG_LABELS.get(code, code.upper())
            self.lang_combo.addItem(label, code)

    def _on_language_changed(self, index: int) -> None:
        code = self.lang_combo.currentData()
        if code:
            self._current_language = code
            self._apply_filter()
            self.languageChanged.emit(code)

    def _apply_filter(self, _gender_text: str | None = None) -> None:
        self.voice_combo.clear()
        lang_code = self.lang_combo.currentData() or "en"
        gender_text = self.gender_combo.currentText()
        gender_map = {"All": None, "Male": VoiceGender.MALE, "Female": VoiceGender.FEMALE}
        target_gender = gender_map.get(gender_text)

        for voice in VOICE_CATALOG:
            if voice.language != lang_code:
                continue
            if target_gender is not None and voice.gender != target_gender:
                continue
            label = f"{voice.name} ({voice.age}, {voice.gender.value})"
            self.voice_combo.addItem(label, voice.id)
        self._update_description()

    def _on_voice_changed(self, index: int) -> None:
        self._update_description()
        voice_id = self.voice_combo.currentData()
        if voice_id:
            self.voiceChanged.emit(voice_id)

    def _update_description(self) -> None:
        voice_id = self.voice_combo.currentData()
        for voice in VOICE_CATALOG:
            if voice.id == voice_id:
                self.desc_label.setText(f"Age {voice.age} — {voice.tone}")
                return
        self.desc_label.setText("")

    def _on_preview(self) -> None:
        voice_id = self.voice_combo.currentData()
        if voice_id:
            self.previewRequested.emit(voice_id)

    def current_voice_id(self) -> str:
        return self.voice_combo.currentData() or DEFAULT_VOICE

    def current_language(self) -> str:
        return self._current_language
