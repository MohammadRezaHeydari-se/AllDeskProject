# AllDeskProject

**A collection of AI-powered desktop applications.**

AllDeskProject is a mono-repository housing multiple production-grade AI desktop applications. Each project is independently packaged, documented, and designed for cross-platform use (Windows, macOS, Linux).

---

## Projects

### VoiceForge

**AI-Powered Speech Synthesis**

VoiceForge generates natural human-like speech from text. Built with PySide6 and edge-tts/gTTS, it features 30 multilingual voice profiles (English, Swedish, Persian), chunk-based generation, GPU acceleration detection, and a professional structured logging system.

```
Location: VoiceForge/src/
Tech: Python 3.12, PySide6, edge-tts, gTTS, Loguru
Status: MVP v1.0
```

→ [VoiceForge README](VoiceForge/README.md)

### ToonForge

**2D Dialogue Scene Generator**

ToonForge is a lightweight web-based animation pipeline for automatic dialogue scene generation. Import character images and audio files, and it auto-generates animated scenes with lip-sync, blinking, and head movement. Built with React/Next.js, FastAPI, and FFmpeg.

```
Location: ToonForge/
Tech: React 18, Next.js 14, FastAPI, FFmpeg, Python 3.12
Status: MVP v1.0
```

→ [ToonForge README](ToonForge/README.md)

---

## Technologies

| Technology | Purpose |
|-----------|---------|
| Python 3.12+ | Core language |
| PySide6 (Qt) | Desktop UI framework |
| XTTS v2 / Coqui TTS | AI speech synthesis |
| ffmpeg / pydub / librosa | Audio processing |
| loguru | Structured JSON logging |
| PyInstaller | Application packaging |

---

## Repository Structure

```
AllDeskProject/
├── VoiceForge/          # AI TTS desktop application
│   └── src/             # Source code (app, core, ui, services, models)
├── ToonForge/           # 2D dialogue scene animation studio
│   ├── backend/         # FastAPI server
│   └── frontend/        # React/Next.js UI
├── README.md            # This file
```

## Development

Each project manages its own dependencies via `requirements.txt` and `pyproject.toml`. To get started with a project:

```bash
cd VoiceForge
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## License

MIT
