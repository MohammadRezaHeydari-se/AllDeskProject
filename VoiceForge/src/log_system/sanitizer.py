from __future__ import annotations

import re
from typing import Any


SENSITIVE_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)(api[_-]?key|apikey|secret|token|password|credential)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(authorization|bearer)\s+\S+"),
    re.compile(r"(?i)sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    re.compile(r"(?i)(private_key|private-key|-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----)"),
]


class LogSanitizer:
    REPLACEMENT = "[REDACTED]"

    @classmethod
    def sanitize(cls, message: str) -> str:
        for pattern in SENSITIVE_PATTERNS:
            message = pattern.sub(cls.REPLACEMENT, message)
        return message

    @classmethod
    def sanitize_record(cls, record: dict[str, Any]) -> dict[str, Any]:
        safe: dict[str, Any] = {}
        for key, value in record.items():
            if isinstance(value, str):
                safe[key] = cls.sanitize(value)
            elif isinstance(value, dict):
                safe[key] = cls.sanitize_record(value)
            else:
                safe[key] = value
        return safe
