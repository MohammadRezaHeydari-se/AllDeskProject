# VoiceForge Setup Guide

## Prerequisites

- **Python 3.12+**
- **ffmpeg** (audio processing)
  - Windows: Download from https://ffmpeg.org/ and add to PATH
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`

## Installation

### 1. Clone and Navigate

```bash
git clone https://github.com/MohammadRezaHeydari-se/AllDeskProject.git
cd AllDeskProject/projects/VoiceForge
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install System Dependencies (Linux)

```bash
sudo apt-get update
sudo apt-get install -y libportaudio2 libsndfile1 espeak-ng
```

### 5. Run the Application

```bash
python main.py
```

## Packaging with PyInstaller

### Linux/macOS

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name VoiceForge main.py
```

### Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name VoiceForge.exe main.py
```

The packaged binary will be in the `dist/` directory.

## Configuration

Config file location: `~/.voiceforge/config.json`

You can modify:
- `default_output_dir` - Default save location
- `default_voice` - Default voice profile
- `theme` - UI theme ("dark" or "light")
- `export_format` - Default audio format (wav/mp3/flac/ogg)
- `gpu_preference` - GPU selection ("auto", "cuda", "metal", "cpu")
