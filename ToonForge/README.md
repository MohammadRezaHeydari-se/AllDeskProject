# ToonForge

A 2D flat-style animation studio for automatic dialogue scene generation. A lightweight animation pipeline for educational and dialogue-based content, inspired by Adobe Character Animator.

## Architecture

```
ToonForge/
├── backend/           # Python/FastAPI server
│   ├── api/           # REST API endpoints
│   ├── core/          # Core logic (audio, scene, render)
│   ├── models/        # Pydantic schemas
│   └── services/      # Business logic
├── frontend/          # React/Next.js UI
│   └── src/
│       ├── api/       # API client
│       ├── components/# UI components
│       └── remotion/  # Remotion compositions
└── config/            # Configuration files
```

## Features

- **Automatic Character Detection** — Maps audio files to characters based on filename prefixes
- **Lip Sync Animation** — Mouth animation driven by audio amplitude analysis
- **Idle Animation** — Natural blinking and subtle head movement
- **Timeline Editor** — Drag-and-drop audio ordering, character reassignment
- **Subtitle Support** — Optional subtitles per audio clip
- **Dual Format Export** — Horizontal (16:9) and vertical (9:16) MP4 output
- **Scene Preview** — Real-time canvas preview of the animation

## Quick Start

### Backend

```bash
cd ToonForge/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd ToonForge/frontend
npm install
npm run dev
```

Open http://localhost:3000

## Usage

1. Click **Import** to add audio files (.wav, .mp3), character images (.png), and a background image
2. Characters are auto-detected from filename prefixes (e.g., `sudabeh_001.wav` → "Sudabeh")
3. Adjust character mapping and audio ordering in the side panel
4. Add optional subtitles to each clip
5. Preview the scene in real-time
6. Click **Export** to render MP4 video

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/projects/` | GET/POST | List/create projects |
| `/api/projects/{id}/import/audio` | POST | Import audio files |
| `/api/projects/{id}/import/characters` | POST | Import character images |
| `/api/projects/{id}/import/background` | POST | Import background |
| `/api/scenes/generate/{id}` | POST | Auto-generate scene |
| `/api/scenes/manifest/{id}` | GET | Get scene manifest |
| `/api/render/export` | POST | Start render job |
| `/api/render/status/{id}` | GET | Check render status |

## Future Roadmap

- Auto camera movement and framing
- Gesture generation for characters
- Emotion detection and expression changes
- AI-generated scene transitions
- Multi-character support (3+)
- Educational slide insertion
- Speech-to-text subtitle generation
- Remotion-based server-side rendering
