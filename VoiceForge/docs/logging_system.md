# VoiceForge Logging System

## Overview

VoiceForge uses a professional structured logging system built on [loguru](https://github.com/Delgan/loguru) with JSON-formatted output for machine parsing and future AI integration.

## Log Files

| File | Level | Purpose |
|------|-------|---------|
| `app.log` | DEBUG+ | All application events |
| `crash.log` | ERROR+ | Critical failures and exceptions |
| `performance.log` | DEBUG+ | Performance metrics (filtered by `perf=True` extra) |

## JSON Log Format

```json
{
  "timestamp": "2025-01-15T10:30:00.123456+00:00",
  "level": "ERROR",
  "module": "tts_engine",
  "function": "generate_audio",
  "line": 42,
  "message": "Primary backend failed: CUDA out of memory",
  "os": "Linux",
  "os_version": "6.2.0-35-generic",
  "exception": "Traceback (most recent call last):\n  ...",
  "voice_id": "female_mid_1",
  "chunk_index": 5,
  "text_length": 1234
}
```

## Log Sanitization

The `LogSanitizer` automatically redacts:
- API keys and tokens (`sk-...`, `api_key=...`)
- Email addresses
- Private keys and certificates
- Passwords and credentials
- Authorization headers

## Log Rotation

Configured via `RotationPolicy`:
- **Max file size**: 50 MB
- **Retention**: 14 days
- **Compression**: gzip
- **Daily rotation**: Yes (at midnight)
- **Max files**: 30

## Usage

```python
from logging.logger import LogManager

# Standard logging
LogManager.app("Generation started")
LogManager.debug("Chunk 3/10 processing", chunk_index=3)
LogManager.error("Failed to load model")

# Performance tracking
LogManager.performance("Generation completed in 12.4s", chunks=10, duration=12.4, text_length=2500)

# Crash logging (automatically goes to crash.log)
LogManager.crash("Unhandled exception in TTS engine")

# Reading logs programmatically
logs = LogManager.get_instance().read_logs("app", lines=50)
```

## Log Viewer (UI)

The built-in Log Center provides:
- Real-time log display (auto-refresh every 5s)
- Three log type tabs (app/crash/performance)
- Detailed JSON view for each entry
- Color-coded severity levels
- Export functionality
- AI analysis placeholder

## AI Debug Integration

The `AIDebugAssistant` prepares compressed debug context for future AI analysis:
- Loads recent log entries
- Extracts stack traces
- Compresses trace data
- Attaches system info
- Exports as structured JSON
