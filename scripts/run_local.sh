#!/usr/bin/env bash
# ==============================================================================
# AI Placement Preparation Agent - Local Development Launcher (macOS/Linux)
# ==============================================================================

set -e

# Colored output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================================================${NC}"
echo -e "${BLUE}   AI Placement Preparation Agent - Local Development Launcher${NC}"
echo -e "${BLUE}==============================================================================${NC}"

# 1. Verify Python Installation
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}[ERROR] Python 3.10+ is required but neither 'python3' nor 'python' was found in PATH.${NC}"
    exit 1
fi

echo -e "${GREEN}[*] Using Python: $($PYTHON_CMD --version)${NC}"

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}[*] Creating virtual environment (.venv)...${NC}"
    $PYTHON_CMD -m venv .venv
fi

echo -e "${GREEN}[*] Activating virtual environment...${NC}"
source .venv/bin/activate

# 3. Environment Configuration
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[*] Generating .env from .env.example (Safe Zero-Cost Mock Mode active)...${NC}"
    cp .env.example .env
fi

# 4. Install Dependencies
echo -e "${GREEN}[*] Checking and installing dependencies...${NC}"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

# 5. Initialize Database & Seed Content
echo -e "${GREEN}[*] Initializing database and indexing knowledge base...${NC}"
python -c "from database.database import init_db; init_db()"
python -m scripts.seed_data
python -c "from app.utils.seed_demo_student import seed_demo_student; seed_demo_student()"

# 6. Launch Streamlit Application
echo ""
echo -e "${BLUE}==============================================================================${NC}"
echo -e "${GREEN}   Application ready! Launching Streamlit at http://localhost:8501${NC}"
echo -e "${YELLOW}   Press Ctrl+C in this terminal window to stop the server.${NC}"
echo -e "${BLUE}==============================================================================${NC}"

streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
