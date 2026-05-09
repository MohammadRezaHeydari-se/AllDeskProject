from __future__ import annotations

from pathlib import Path

import pytest

from core.text_analyzer import TextAnalyzer, MAX_CHARS
from core.chunk_processor import ChunkProcessor


class TestTextAnalyzer:
    def setup_method(self) -> None:
        self.analyzer = TextAnalyzer()

    def test_empty_text(self) -> None:
        result = self.analyzer.analyze("")
        assert not result.is_valid
        assert "empty" in result.errors[0].lower()

    def test_valid_text(self) -> None:
        text = "Hello world. This is a test."
        result = self.analyzer.analyze(text)
        assert result.is_valid
        assert result.char_count == len(text)
        assert result.word_count == 6
        assert result.sentence_count == 2

    def test_text_too_long(self) -> None:
        text = "A" * (MAX_CHARS + 1)
        result = self.analyzer.analyze(text)
        assert not result.is_valid

    def test_paragraph_split(self) -> None:
        text = "First paragraph.\n\nSecond paragraph."
        result = self.analyzer.analyze(text)
        assert result.paragraph_count == 2


class TestChunkProcessor:
    def setup_method(self) -> None:
        self.processor = ChunkProcessor(max_chunk_chars=50)

    def test_chunk_creation(self) -> None:
        sentences = ["This is a test sentence.", "Another one here.", "And a third sentence for testing purposes."]
        paragraphs = ["This is a test sentence. Another one here."]
        chunks = self.processor.process(sentences, paragraphs)
        assert len(chunks) >= 1
        assert all(c.char_count > 0 for c in chunks)

    def test_empty_input(self) -> None:
        chunks = self.processor.process([], [])
        assert len(chunks) == 0


if __name__ == "__main__":
    pytest.main([__file__])
