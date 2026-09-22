@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo    AI Placement Preparation Agent - Local Development Launcher (Windows)
echo ==============================================================================

:: 1. Verify Python Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.10+ is required but not found in PATH.
    echo Please install Python from https://www.python.org/
    exit /b 1
)

:: 2. Setup Virtual Environment
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
)

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat

:: 3. Environment Configuration
if not exist ".env" (
    echo [*] Generating .env from .env.example (Safe Zero-Cost Mock Mode active)...
    copy .env.example .env >nul
)

:: 4. Install Dependencies
echo [*] Checking and installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

:: 5. Initialize Database & Seed Content
echo [*] Initializing database and indexing knowledge base...
python -c "from database.database import init_db; init_db()"
python -m scripts.seed_data
python -c "from app.utils.seed_demo_student import seed_demo_student; seed_demo_student()"

:: 6. Launch Streamlit Application
echo.
echo ==============================================================================
echo    Application ready! Launching Streamlit at http://localhost:8501
echo    Press Ctrl+C in this terminal window to stop the server.
echo ==============================================================================
streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0

pause
