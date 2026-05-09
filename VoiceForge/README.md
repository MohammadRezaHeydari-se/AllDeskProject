# VoiceForge

**AI-Powered Cross-Platform Desktop TTS Application**

VoiceForge is a production-grade text-to-speech desktop application supporting English, Swedish, and Persian with 30 voice personas.

## Architecture

```
Input → Text Parser → Chunking Engine → Voice Engine → Audio Processor → Exporter
```

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| **Entry** | `src/main.py` | Sets `sys.path`, invokes `app.main.main()` |
| **App** | `src/app/` | `QApplication`, main window, lifecycle |
| **Core** | `src/core/` | TTS engine (edge-tts, gTTS), text analysis, chunking |
| **UI** | `src/ui/` | PySide6 components: voice selector, output settings, audio player |
| **Services** | `src/services/` | Config management, GPU detection, dependency checks |
| **Models** | `src/models/` | Voice profiles, configuration schemas |
| **Logging** | `src/log_system/` | Structured JSON logging with Loguru |

## Tech Stack

- **Python 3.12+** — Core language
- **PySide6** — Desktop UI framework
- **edge-tts** — Primary TTS backend (30 voices, SSML emotional styles)
- **gTTS** — Fallback TTS backend
- **pydub / librosa / ffmpeg** — Audio processing
- **loguru** — Structured JSON logging
- **pytest** — Unit testing

## Quick Start

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Features

- 30 multilingual voice profiles (10 English, 10 Swedish, 10 Persian)
- Speed control slider (50%–200%)
- SSML emotional styles (sad, cheerful, angry, fearful, excited, etc.)
- Language-aware sentence splitting
- Custom file naming with auto-increment
- Dark theme UI
- Retry logic with exponential backoff for network issues
