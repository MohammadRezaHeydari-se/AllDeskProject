from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

from log_system.logger import LogManager

MAX_CHUNK_CHARS = 300


@dataclass
class Chunk:
    index: int
    text: str
    char_count: int
    is_paragraph_start: bool = False


class ChunkProcessor:
    def __init__(self, max_chunk_chars: int = MAX_CHUNK_CHARS) -> None:
        self.max_chunk_chars = max_chunk_chars

    def process(self, sentences: list[str], paragraphs: list[str]) -> list[Chunk]:
        chunks: list[Chunk] = []
        current_text = ""
        chunk_index = 0
        paragraph_set = set(paragraphs)

        for sentence in sentences:
            if len(current_text) + len(sentence) + 1 > self.max_chunk_chars and current_text:
                is_para_start = current_text.strip() in paragraph_set
                chunks.append(Chunk(
                    index=chunk_index,
                    text=current_text.strip(),
                    char_count=len(current_text.strip()),
                    is_paragraph_start=is_para_start,
                ))
                chunk_index += 1
                current_text = sentence
            else:
                if current_text:
                    current_text += " " + sentence
                else:
                    current_text = sentence

        if current_text.strip():
            is_para_start = current_text.strip() in paragraph_set
            chunks.append(Chunk(
                index=chunk_index,
                text=current_text.strip(),
                char_count=len(current_text.strip()),
                is_paragraph_start=is_para_start,
            ))

        LogManager.debug(f"Chunking complete: {len(chunks)} chunks created", chunk_count=len(chunks))
        return chunks

    @staticmethod
    def iter_chunks(chunks: list[Chunk]) -> Iterator[Chunk]:
        yield from chunks
