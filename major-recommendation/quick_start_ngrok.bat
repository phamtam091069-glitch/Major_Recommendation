@echo off
REM Quick Start Script for Ngrok Deployment
REM This script helps you deploy the Flask app publicly with Ngrok

echo.
echo ========================================
echo   MAJOR RECOMMENDATION - NGROK DEPLOY
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Check if Flask app is ready
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Please run this script from the project root directory.
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Flask not installed. Installing now...
    pip install -r requirements.txt
)

echo [2/4] Starting Flask app...
echo.
echo Starting on http://127.0.0.1:5000
echo.
echo Press CTRL+C to stop.
echo.
pause

python app.py
