#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "=== ToonForge - Backend ==="
echo ""

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if ! pip show fastapi > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "Starting FastAPI server on http://localhost:8000"
echo "API docs at http://localhost:8000/docs"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
