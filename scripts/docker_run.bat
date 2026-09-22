@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo    AI Placement Preparation Agent - Docker Container Launcher (Windows)
echo ==============================================================================

:: 1. Verify Docker CLI
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not in PATH.
    echo Please start Docker Desktop or install Docker from https://www.docker.com/
    exit /b 1
)

:: 2. Ensure data directory exists
if not exist "data" (
    mkdir data
)

:: 3. Build & Run via Docker Compose
echo [*] Building image and starting container...
docker compose up --build -d

echo.
echo ==============================================================================
echo    Container running! Access the UI at: http://localhost:8501
echo    View logs:  docker compose logs -f
echo    Stop:       docker compose down
echo ==============================================================================
