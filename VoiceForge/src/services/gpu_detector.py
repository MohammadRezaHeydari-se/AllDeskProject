from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass, field
from enum import Enum


class GPUType(Enum):
    CUDA = "cuda"
    METAL = "metal"
    CPU = "cpu"
    UNKNOWN = "unknown"


@dataclass
class GPUInfo:
    gpu_type: GPUType = GPUType.UNKNOWN
    name: str = ""
    available: bool = False
    version: str = ""
    memory_gb: float = 0.0
    extra: dict = field(default_factory=dict)


class GPUDetector:
    @staticmethod
    def detect() -> GPUInfo:
        system = platform.system()
        info = GPUInfo()

        if system == "Windows":
            info = GPUDetector._check_cuda() or GPUDetector._check_cpu()
        elif system == "Darwin":
            info = GPUDetector._check_metal() or GPUDetector._check_cpu()
        elif system == "Linux":
            info = GPUDetector._check_cuda() or GPUDetector._check_cpu()

        return info

    @staticmethod
    def _check_cuda() -> GPUInfo | None:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(",")
                name = parts[0].strip() if parts else "NVIDIA GPU"
                memory_str = parts[1].strip().replace("MiB", "").strip() if len(parts) > 1 else "0"
                try:
                    memory_gb = float(memory_str) / 1024
                except ValueError:
                    memory_gb = 0.0
                return GPUInfo(gpu_type=GPUType.CUDA, name=name, available=True, memory_gb=memory_gb, version="cuda")
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return None
        return None

    @staticmethod
    def _check_metal() -> GPUInfo | None:
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "Chipset Model" in line or "Metal" in line:
                        name = line.split(":")[-1].strip()
                        return GPUInfo(gpu_type=GPUType.METAL, name=name, available=True, version="metal")
        except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return None
        return None

    @staticmethod
    def _check_cpu() -> GPUInfo:
        return GPUInfo(gpu_type=GPUType.CPU, name=f"{platform.processor() or 'CPU'}", available=True, version="cpu")
