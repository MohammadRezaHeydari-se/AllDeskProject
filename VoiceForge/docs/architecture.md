# VoiceForge Architecture

## Overview

VoiceForge uses a **pipeline-based architecture** where data flows through a series of modular, interchangeable stages. This design ensures scalability, testability, and future extensibility.

## Pipeline Flow

```
Input (Text)
    |
    v
Text Analyzer    -- Validates input, splits into sentences/paragraphs
    |
    v
Chunk Processor  -- Divides text into processable chunks (300 chars each)
    |
    v
Voice Planner    -- Selects voice profile, configures speed/pitch/emotion
    |
    v
TTS Engine       -- Generates audio via XTTS v2 (with Coqui TTS fallback)
    |
    v
Audio Processor  -- Merges chunks, normalizes, converts formats
    |
    v
Exporter         -- Writes final audio to user-specified location
```

## Layer Architecture

### Core Layer (`core/`)
- `TextAnalyzer` - Input validation, sentence/paragraph detection
- `ChunkProcessor` - Text chunking with overlap for seamless transitions
- `VoicePlanner` - Voice profile selection and configuration
- `TTSEngine` - TTS backend abstraction (primary + fallback)
- `AudioProcessor` - Audio merging, normalization, format conversion
- `Exporter` - File output management

### Services Layer (`services/`)
- `ConfigManager` - Singleton config persistence (JSON ~/.voiceforge/)
- `GPUDetector` - CUDA/Metal/CPU auto-detection
- `DependencySetup` - Cross-platform dependency preparation
- `AIDebugAssistant` - Placeholder for future AI debugging integration

### UI Layer (`ui/`)
- `MainWindow` - Application shell with split-panel layout
- Widgets:
  - `VoiceSelector` - Gender/voice/age selection with preview
  - `TextEditor` - Input with 5000-char limit and counter
  - `AudioControls` - Play/pause/stop/seek controls
  - `ProgressSection` - Progress bar with ETA estimation
  - `OutputSettings` - Directory browser and format selector
  - `LogCenter` - Real-time log viewer with AI analysis placeholder

### Logging Layer (`log_system/`)
- `LogManager` - Singleton loguru-based manager
- `LogSanitizer` - PII/secret redaction
- `RotationPolicy` - Configurable rotation rules
- Three log streams: `app.log`, `crash.log`, `performance.log`

## Design Decisions

1. **Pipeline pattern** - Each stage is independently testable and replaceable
2. **Singleton services** - ConfigManager and LogManager use singletons for global access
3. **Protocol-based backends** - TTS backends implement a Protocol for easy swapping
4. **QThread for generation** - Heavy TTS work runs off the main thread
5. **Chunk-based generation** - Prevents memory issues with large texts
6. **JSON structured logging** - Machine-parseable logs for future AI analysis

## Future Extensions

The architecture supports adding:
- PDF/DOCX/EPUB narrators as new pipeline input stages
- Emotion analysis as a VoicePlanner extension
- Voice cloning as a new backend
- Multi-speaker narration by extending VoicePlanner
- Multi-language via localized TextAnalyzers
