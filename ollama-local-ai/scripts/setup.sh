#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
err()   { echo -e "${RED}[ERROR]${NC} $1"; }

echo ""
echo "============================================"
echo "  Ollama Local AI — One-Time Setup"
echo "============================================"
echo ""

# ── Check prerequisites ────────────────────────────────────────────────

if ! command -v python3 &>/dev/null; then
    err "Python 3 is required. Install it from python.org or via Homebrew:"
    echo "    brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
info "Python version: $PYTHON_VERSION"

# ── Ollama ─────────────────────────────────────────────────────────────

if ! command -v ollama &>/dev/null; then
    info "Installing Ollama via Homebrew..."
    brew install ollama
else
    ok "Ollama already installed"
fi

if ! pgrep -x "ollama" &>/dev/null && ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
    info "Starting Ollama server..."
    ollama serve &>/dev/null &
    OLLAMA_PID=$!
    sleep 3
fi

info "Pulling llama3.1:8b (this may take a few minutes on first run)..."
ollama pull llama3.1:8b
ok "llama3.1:8b ready"

info "Pulling nomic-embed-text..."
ollama pull nomic-embed-text
ok "nomic-embed-text ready"

# ── Backend ────────────────────────────────────────────────────────────

info "Setting up Python backend..."
cd "$PROJECT_DIR/backend"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt
ok "Backend dependencies installed"

# ── Frontend ───────────────────────────────────────────────────────────

if command -v node &>/dev/null; then
    NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
else
    NODE_VERSION=0
fi

if [ "$NODE_VERSION" -lt 18 ]; then
    if [ -s "$HOME/.nvm/nvm.sh" ]; then
        source "$HOME/.nvm/nvm.sh"
        if nvm ls 22 &>/dev/null; then
            nvm use 22
        elif nvm ls 20 &>/dev/null; then
            nvm use 20
        elif nvm ls 18 &>/dev/null; then
            nvm use 18
        else
            info "Installing Node 22 via nvm..."
            nvm install 22
            nvm use 22
        fi
    else
        err "Node.js 18+ is required. Install via nvm or nodejs.org"
        exit 1
    fi
fi

info "Setting up React frontend..."
cd "$PROJECT_DIR/frontend"
npm install --silent
npm run build
ok "Frontend built"

# ── macOS App Bundle ───────────────────────────────────────────────────

info "Creating macOS app bundle..."
"$SCRIPT_DIR/create-app.sh"
ok "App bundle created"

# ── Done ───────────────────────────────────────────────────────────────

echo ""
echo "============================================"
echo -e "  ${GREEN}Setup complete!${NC}"
echo ""
echo "  To launch the app:"
echo "    1. Double-click 'Ollama Local AI.app' in the scripts/ folder"
echo "    2. Or run: ./scripts/start.sh"
echo "============================================"
echo ""
