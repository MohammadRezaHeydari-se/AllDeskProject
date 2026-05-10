import numpy as np
import librosa


def analyze_amplitude(filepath: str, fps: int = 30) -> list[float]:
    y, sr = librosa.load(filepath, sr=22050)
    hop_length = int(sr / fps)
    frames = librosa.util.frame(y, frame_length=hop_length * 2, hop_length=hop_length)
    rms = np.sqrt(np.mean(frames ** 2, axis=0))
    smoothed = _smooth_amplitude(rms, window=3)
    normalized = _normalize_amplitude(smoothed)
    return normalized.tolist()


def _smooth_amplitude(data: np.ndarray, window: int = 3) -> np.ndarray:
    kernel = np.ones(window) / window
    return np.convolve(data, kernel, mode="same")


def _normalize_amplitude(data: np.ndarray) -> np.ndarray:
    if data.max() == 0:
        return data
    normalized = data / data.max()
    return np.clip(normalized, 0.0, 1.0)


def detect_speech_segments(filepath: str, threshold_db: float = -30.0) -> list[tuple[float, float]]:
    y, sr = librosa.load(filepath, sr=22050)
    intervals = librosa.effects.split(y, top_db=abs(threshold_db))
    segments = []
    for start, end in intervals:
        segments.append((start / sr, end / sr))
    return segments


def get_audio_duration(filepath: str) -> float:
    y, sr = librosa.load(filepath, sr=None)
    return float(len(y) / sr)


def analyze_phoneme_levels(filepath: str, fps: int = 30) -> list[dict]:
    y, sr = librosa.load(filepath, sr=22050)
    hop_length = int(sr / fps)

    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]

    rms = np.sqrt(np.mean(librosa.util.frame(y, frame_length=hop_length * 2, hop_length=hop_length) ** 2, axis=0))

    frames_data = []
    for i in range(len(rms)):
        frames_data.append({
            "amplitude": float(rms[i]),
            "mouth_open": float(np.clip(rms[i] * 3.0, 0.0, 1.0)),
            "energy": float(spectral_centroids[i]) if i < len(spectral_centroids) else 0.0,
        })

    return _smooth_phoneme_data(frames_data)


def _smooth_phoneme_data(data: list[dict], window: int = 2) -> list[dict]:
    if len(data) < window * 2 + 1:
        return data
    smoothed = []
    for i in range(len(data)):
        start = max(0, i - window)
        end = min(len(data), i + window + 1)
        avg_mouth = sum(d["mouth_open"] for d in data[start:end]) / (end - start)
        entry = data[i].copy()
        entry["mouth_open"] = avg_mouth
        smoothed.append(entry)
    return smoothed
