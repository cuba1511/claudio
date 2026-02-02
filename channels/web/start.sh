#!/bin/bash

# Start Claudio Web Dashboard
# Usage: ./start.sh [--dev]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$SCRIPT_DIR"

# Check if venv exists at project root
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
fi

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Start server
if [ "$1" == "--dev" ]; then
    echo "🚀 Starting Claudio Dashboard in development mode..."
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
else
    echo "🚀 Starting Claudio Dashboard..."
    uvicorn app:app --host 0.0.0.0 --port 8000
fi
