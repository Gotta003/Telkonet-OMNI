#!/usr/bin/env bash
#===============================================
# 1. Bridge Server (app.py) -> background
# 2. Reception GUI (gui-reception) -> background
# 3. Browser (http://127.0.0.1:5000) -> after bridge is ready
#
# Options:
# `./launch.sh --no-browser` skip opening the browser
# `./launch.sh --bridge-only` start only the bridge
# `./launch.sh --reception` start only reception GUI  
#===============================================

chmod +x setup.sh
./setup.sh

set -e
#Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

#Config
BRIDGE_PORT=5000
LOCAL_IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
if [ -z "$LOCAL_IP" ]; then
    BRIDGE_HOST="127.0.0.1"
else
    BRIDGE_HOST="$LOCAL_IP"
fi

BRIDGE_URL="http://${BRIDGE_HOST}:${BRIDGE_PORT}"
BRIDGE_WAIT=4          # seconds to wait for Flask to start
LOG_DIR="logs"
BRIDGE_LOG="${LOG_DIR}/bridge.log"
RECEPTION_LOG="${LOG_DIR}/reception.log"

#ARGS
OPEN_BROWSER=true
START_BRIDGE=true
START_RECEPTION=true

for arg in "$@"; do
    case $arg in
        --no-browser) OPEN_BROWSER=false ;;
        --bridge-only) START_RECEPTION=false ;;
        --reception) START_BRIDGE=false; OPEN_BROWSER=false ;;
    esac
done

log()     { echo -e "${CYAN}[OMNI]${NC} $*"; }
success() { echo -e "${GREEN}[✓]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*"; }

open_browser() {
    local url=$1
    if command -v xdg-open &>/dev/null; then
        xdg-open "$url" &
    elif command -v open &>/dev/null; then
        open "$url"
    elif command -v start &>/dev/null; then
        start "$url"
    else
        warn "Could not detect browser opener - visit $url manually"
    fi
}

wait_for_port() {
    local port=$1
    local name=$2
    local max=20
    local i=0
    while ! nc -z 127.0.0.1 "$port" 2>/dev/null; do
        sleep 0.5
        i=$((i+1))
        if [ $i -ge $max ]; then
            error "$name did not start in time on port $port"
            return 1
        fi
    done
    return 0
}

cleanup() {
    echo ""
    log "Shutting down..."
    [ -n "$BRIDGE_PID" ] && kill -- -"$BRIDGE_PID" 2>/dev/null || true
    [ -n "$RECEPTION_PID" ] && kill -- -"$RECEPTION_PID" 2>/dev/null || true
    success "All processes stopped"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo ""
echo -e "${BOLD}${BLUE}  TELKONET OMNI${NC}${BOLD}  Room Controller${NC}"
echo -e "  ─────────────────────────────────"

#Python
if ! command -v python3 &>/dev/null & ! command -v python &>/dev/null; then
    error "Python not found. Install Python 3.10+"
    exit 1
fi
PYTHON=$(command -v python3 || command -v python)
PY_VER=$($PYTHON --version 2>&1)
success "Python: $PY_VER"

$PYTHON -c "import flask, serial" 2>/dev/null \
    && success "Python packages: OK" \
    || warn "Some packages may be missing - run pip install -r requirements.txt"
mkdir -p "$LOG_DIR"

if lsof -t -i:$BRIDGE_PORT &>/dev/null; then
    warn "Port $BRIDGE_PORT is occupied. Cleaning ghost background workers..."
    kill -9 $(lsof -t -i:$BRIDGE_PORT) 2>/dev/null || true
    sleep 1
fi

#Start Bridge
if $START_BRIDGE; then
    log "Starting bridge server..."
    if nc -z 127.0.0.1 "$BRIDGE_PORT" 2>/dev/null; then
        warn "Port $BRIDGE_PORT already in use -skipping bridge start"
        BRIDGE_PID=""
    else
        setsid $PYTHON bridge/app.py > "$BRIDGE_LOG" 2>&1 & BRIDGE_PID=$!
        log "Bridge PID: $BRIDGE_PID (log: $BRIDGE_LOG)"
        log "Waiting for bridge on port $BRIDGE_PORT..."
        if wait_for_port "$BRIDGE_PORT" "Bridge"; then
            success "Bridge running -> $BRIDGE_URL"
        else
            error "Bridge failed to start. Check $BRIDGE_LOG"
            exit 1
        fi
    fi
fi

if $START_RECEPTION; then
    if $PYTHON -c "import tkinter" 2>/dev/null; then
        log "Starting Reception GUI..."
        setsid $PYTHON gui-reception/main.py > "$RECEPTION_LOG" 2>&1 & RECEPTION_PID=$!
        success "Reception GUI PID: $RECEPTION_PID (log: $RECEPTION_LOG)"
    else
        warn "tkinter not available - skipping reception GUI"
        RECEPTION_PID=""
    fi
fi

echo ""
echo -e " ${BOLD}Running:${NC}"
$START_BRIDGE    && echo -e "  ${GREEN}●${NC} Bridge      → ${BLUE}$BRIDGE_URL${NC}  (log: $BRIDGE_LOG)"
$OPEN_BROWSER    && echo -e "  ${GREEN}●${NC} Browser     → ${BLUE}$BRIDGE_URL${NC}"
$START_RECEPTION && echo -e "  ${GREEN}●${NC} Reception   → Tkinter window  (log: $RECEPTION_LOG)"
echo ""
echo -e "  ${YELLOW}Press Ctrl+C to stop all processes${NC}"
echo ""

while true; do
    sleep 2
    if $START_BRIDGE && [ -n "$BRIDGE_PID" ]; then
        if ! kill -0 "$BRIDGE_PID" 2>/dev/null; then
            error "Bridge process died unexpectedly - check $BRIDGE_LOG"
            $START_RECEPTION && kill -- -"$RECEPTION_PID" 2>/dev/null || true
            exit 1
        fi
    fi
    if $START_RECEPTION && [ -n "$RECEPTION_PID" ]; then
        if ! kill -0 "$RECEPTION_PID" 2>/dev/null; then
            warn "Reception GUI closed"
            RECEPTION_PID=""
        fi
    fi
done