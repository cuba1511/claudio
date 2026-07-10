#!/usr/bin/env bash
# AlphaEngine AI — FastAPI + HTML
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$SCRIPT_DIR"

if [ -d "$PROJECT_ROOT/venv" ]; then
  # shellcheck source=/dev/null
  source "$PROJECT_ROOT/venv/bin/activate"
fi

if ! python -c "import fastapi" 2>/dev/null; then
  echo "Installing alphaengine dependencies..."
  pip install -r requirements.txt
fi

echo "AlphaEngine AI → http://127.0.0.1:8501"
exec uvicorn app:app --host 127.0.0.1 --port 8501
