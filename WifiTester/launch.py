#!/usr/bin/env python3
"""
NetGuard launcher — auto-detects OS and elevates privileges if needed.

Usage:
    python launch.py          # normal run
    python launch.py --debug  # run without root elevation
"""
import sys
import os
import subprocess
import platform

VENV_PYTHON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "bin", "python")
SRC_MAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "main.py")


def get_python() -> str:
    if os.path.exists(VENV_PYTHON):
        return VENV_PYTHON
    return sys.executable


def main():
    system = platform.system()
    python = get_python()

    if "--debug" in sys.argv:
        os.execv(python, [python, SRC_MAIN])

    # Check if already root
    if os.geteuid() == 0 if hasattr(os, "geteuid") else True:
        os.execv(python, [python, SRC_MAIN])

    if system in ("Linux", "Darwin"):
        cmd = ["sudo", python, SRC_MAIN]
    elif system == "Windows":
        cmd = ["runas", "/user:Administrator", python, SRC_MAIN]
    else:
        cmd = [python, SRC_MAIN]

    try:
        subprocess.run(cmd, check=True)
    except FileNotFoundError:
        print(f"[NetGuard] Could not elevate privileges. Try: sudo {python} {SRC_MAIN}")
        sys.exit(1)
    except subprocess.CalledProcessError:
        sys.exit(1)


if __name__ == "__main__":
    main()
