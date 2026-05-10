# AllDeskProject

A collection of diverse projects — including desktop apps, web applications, CLI tools, mobile apps, scripts, and anything else worth building.

---

## Projects

### VoiceForge

**Text-to-Speech Desktop Application**

VoiceForge is a cross-platform desktop application for generating speech from text. It supports 30 multilingual voice profiles (English, Swedish, Persian), chunk-based processing, GPU acceleration detection, and structured logging.

- **Location:** `VoiceForge/`
- **Technologies:** Python 3.12, PySide6, edge-tts, gTTS, Loguru
- **Status:** MVP v1.0

→ [VoiceForge README & Documentation](VoiceForge/README.md)

---

### ToonForge

**2D Dialogue Scene Animation Studio**

ToonForge is a web-based animation pipeline for automatic dialogue scene generation. Import character images and audio files to generate animated scenes with lip-sync, blinking, and head movement. Features a timeline editor, dual-format MP4 export (16:9 / 9:16), and real-time scene preview.

- **Location:** `ToonForge/`
- **Technologies:** React 18, Next.js 14, FastAPI, FFmpeg, Python 3.12
- **Status:** MVP v1.0

→ [ToonForge README & Documentation](ToonForge/README.md)

---

## Repository Structure

```
AllDeskProject/
├── VoiceForge/          # Text-to-Speech desktop application
│   └── src/             # Source code (app, core, ui, services, models)
├── ToonForge/           # 2D dialogue scene animation studio
│   ├── backend/         # FastAPI server
│   └── frontend/        # React/Next.js UI
└── README.md            # This file
```

## Development

Each project manages its own dependencies. Refer to each project's README for setup instructions.

## License

MIT
