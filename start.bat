@echo off
title CommAI - Email Analyzer Server
color 0A

:: Ensure we are in the script's directory
cd /d "%~dp0"

echo ========================================
echo    CommAI - Email Analyzer
echo    Starting Server...
echo ========================================
echo.

REM Check if .env file exists, if not create from example
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env file from .env.example...
        copy .env.example .env
        echo Please edit .env file with your configuration
        echo.
    )
)

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

echo.
echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo Downloading TextBlob corpora...
python -m textblob.download_corpora

echo.
echo ========================================
echo    Server Starting on Port 8000
echo    Opening Browser...
echo ========================================
echo.
echo Environment: Using .env file for configuration
echo Logs: Check commai.log for detailed logs
echo.
echo Press Ctrl+C to stop the server
echo.

:: Open the browser
start "" http://localhost:8000

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
