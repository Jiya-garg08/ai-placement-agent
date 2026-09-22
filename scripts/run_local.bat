@echo off

:: 1. Navigate to repository root directory
cd /d "%~dp0.."

echo ==============================================================================
echo    AI Placement Preparation Agent - Local Development Launcher (Windows)
echo ==============================================================================

:: 2. Verify Python Installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is required but was not found in PATH.
    echo Please install Python from https://www.python.org/
    exit /b 1
)

:: 3. Setup Virtual Environment
if not exist ".venv" (
    echo [*] Creating virtual environment .venv ...
    python -m venv .venv
)

echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat
set PYTHONPATH=%cd%;%PYTHONPATH%

:: 4. Environment Configuration
if not exist ".env" (
    echo [*] Generating .env from .env.example ...
    copy .env.example .env >nul
)

:: 5. Install Dependencies
echo [*] Checking and installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

:: 6. Initialize Database and Seed Content
echo [*] Initializing database and indexing knowledge base...
python -c "from database.database import init_db; init_db()"
python -m scripts.seed_data
python -c "from app.utils.seed_demo_student import seed_demo_student; seed_demo_student()"

:: 7. Launch Streamlit Application
echo.
echo ==============================================================================
echo    Application ready! Launching Streamlit at http://localhost:8501
echo    Press Ctrl+C in this terminal window to stop the server.
echo ==============================================================================
streamlit run app/streamlit_app.py --server.port=8501 --server.address=0.0.0.0

pause
