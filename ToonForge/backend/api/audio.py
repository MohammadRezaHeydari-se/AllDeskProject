from fastapi import APIRouter, HTTPException
from models.schemas import AudioClip
from core.audio_analysis import get_audio_duration, analyze_amplitude

router = APIRouter()


@router.get("/analyze")
async def analyze_audio(filepath: str):
    import os
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    duration = get_audio_duration(filepath)
    amplitude = analyze_amplitude(filepath)
    return {
        "duration": duration,
        "amplitude_frames": amplitude[:1000],
        "total_frames": len(amplitude),
        "sample_rate": 22050,
    }
