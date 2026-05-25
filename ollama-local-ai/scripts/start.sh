#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

BACKEND_PID=""
PORT=8000

cleanup() {
    echo ""
    echo -e "${BLUE}[INFO]${NC}  Shutting down..."
    if [ -n "$BACKEND_PID" ]; then
        kill "$BACKEND_PID" 2>/dev/null
    fi
    echo -e "${GREEN}[OK]${NC}    Stopped. Goodbye!"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo ""
echo "  ╔═══════════════════════════════════╗"
echo "  ║       Ollama Local AI             ║"
echo "  ╚═══════════════════════════════════╝"
echo ""

# ── Ensure Ollama is running ───────────────────────────────────────────

if curl -sf http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${GREEN}[OK]${NC}    Ollama server is running"
elif command -v ollama &>/dev/null; then
    echo -e "${BLUE}[INFO]${NC}  Starting Ollama..."
    if [ -d "/Applications/Ollama.app" ]; then
        open -a Ollama
    else
        ollama serve &>/dev/null &
    fi
    for i in $(seq 1 30); do
        if curl -sf http://localhost:11434/api/tags &>/dev/null; then
            break
        fi
        sleep 1
    done
    if curl -sf http://localhost:11434/api/tags &>/dev/null; then
        echo -e "${GREEN}[OK]${NC}    Ollama server started"
    else
        echo -e "${RED}[ERROR]${NC} Ollama failed to start after 30s"
        exit 1
    fi
else
    echo -e "${RED}[ERROR]${NC} Ollama is not installed. Run setup.sh first."
    exit 1
fi

# ── Check models ───────────────────────────────────────────────────────

if ! ollama list | grep -q "llama3.1:8b"; then
    echo -e "${BLUE}[INFO]${NC}  Model llama3.1:8b not found. Pulling..."
    ollama pull llama3.1:8b
fi

# ── Activate Python venv ──────────────────────────────────────────────

if [ ! -d "$PROJECT_DIR/backend/venv" ]; then
    echo -e "${RED}[ERROR]${NC} Backend venv not found. Run setup.sh first."
    exit 1
fi

source "$PROJECT_DIR/backend/venv/bin/activate"

# ── Check frontend build ──────────────────────────────────────────────

if [ ! -f "$PROJECT_DIR/frontend/dist/index.html" ]; then
    echo -e "${BLUE}[INFO]${NC}  Frontend not built. Building now..."
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh"
        nvm use 22 2>/dev/null || nvm use 20 2>/dev/null || nvm use 18 2>/dev/null
    fi
    cd "$PROJECT_DIR/frontend" && npm run build
fi

# ── Start FastAPI (serves API + built frontend) ───────────────────────

echo -e "${BLUE}[INFO]${NC}  Starting server on http://localhost:$PORT"

cd "$PROJECT_DIR/backend"
uvicorn app.main:app --host 127.0.0.1 --port $PORT &
BACKEND_PID=$!

sleep 2

if kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo -e "${GREEN}[OK]${NC}    Server running at http://localhost:$PORT"
else
    echo -e "${RED}[ERROR]${NC} Server failed to start"
    exit 1
fi

# ── Open browser ──────────────────────────────────────────────────────

open "http://localhost:$PORT"

echo ""
echo -e "  ${GREEN}Ready!${NC} App is open in your browser."
echo "  Press Ctrl+C to stop."
echo ""

# Keep running until Ctrl+C
wait "$BACKEND_PID"
