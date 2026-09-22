#!/usr/bin/env bash
# ==============================================================================
# AI Placement Preparation Agent - Docker Container Launcher (macOS/Linux)
# ==============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}   AI Placement Preparation Agent - Docker Container Launcher${NC}"
echo -e "${BLUE}==============================================================================${NC}"

# 1. Verify Docker CLI
if ! command -v docker &>/dev/null; then
    echo -e "${RED}[ERROR] Docker is not installed or not in PATH.${NC}"
    echo "Please install Docker from https://www.docker.com/"
    exit 1
fi

# 2. Ensure data directory exists
mkdir -p data

# 3. Build & Run via Docker Compose
echo -e "${GREEN}[*] Building image and starting container...${NC}"
docker compose up --build -d

echo ""
echo -e "${BLUE}==============================================================================${NC}"
echo -e "${GREEN}   Container running! Access the UI at: http://localhost:8501${NC}"
echo -e "   View logs:  docker compose logs -f"
echo -e "   Stop:       docker compose down"
echo -e "${BLUE}==============================================================================${NC}"
