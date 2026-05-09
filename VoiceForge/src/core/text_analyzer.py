from __future__ import annotations

import re
from dataclasses import dataclass, field

from log_system.logger import LogManager

PARAGRAPH_PATTERN = re.compile(r"\n\s*\n")
MAX_CHARS = 5000

SENTENCE_PATTERNS: dict[str, re.Pattern] = {
    "en": re.compile(r"(?<=[.!?])\s+(?=[A-Z])"),
    "fa": re.compile(r"(?<=[.!?؟])\s+"),
}

DEFAULT_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")


@dataclass
class TextAnalysis:
    original: str
    paragraphs: list[str] = field(default_factory=list)
    sentences: list[str] = field(default_factory=list)
    char_count: int = 0
    word_count: int = 0
    paragraph_count: int = 0
    sentence_count: int = 0
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)


class TextAnalyzer:
    def analyze(self, text: str, language: str = "en") -> TextAnalysis:
        analysis = TextAnalysis(original=text)
        analysis.char_count = len(text)
        analysis.word_count = len(text.split())

        if not text or not text.strip():
            analysis.is_valid = False
            analysis.errors.append("Text is empty.")
            LogManager.warning("Empty text submitted for analysis")
            return analysis

        if analysis.char_count > MAX_CHARS:
            analysis.is_valid = False
            analysis.errors.append(f"Text exceeds {MAX_CHARS} characters ({analysis.char_count}).")
            LogManager.warning(f"Text too long: {analysis.char_count} chars (max {MAX_CHARS})")
            return analysis

        raw_paragraphs = PARAGRAPH_PATTERN.split(text.strip())
        analysis.paragraphs = [p.strip() for p in raw_paragraphs if p.strip()]
        analysis.paragraph_count = len(analysis.paragraphs)

        pattern = SENTENCE_PATTERNS.get(language, DEFAULT_SENTENCE_PATTERN)
        all_sentences: list[str] = []
        for para in analysis.paragraphs:
            sentences = pattern.split(para)
            for s in sentences:
                s = s.strip()
                if s:
                    all_sentences.append(s)
        analysis.sentences = all_sentences
        analysis.sentence_count = len(all_sentences)

        LogManager.debug(
            f"Text analyzed: {analysis.char_count} chars, {analysis.word_count} words, "
            f"{analysis.paragraph_count} paragraphs, {analysis.sentence_count} sentences",
            char_count=analysis.char_count,
            word_count=analysis.word_count,
            sentence_count=analysis.sentence_count,
        )
        return analysis
