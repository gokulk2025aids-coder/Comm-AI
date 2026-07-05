@echo off
title CommAI - Run Tests
color 0B

echo ========================================
echo    CommAI - Test Suite
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Installing test dependencies...
pip install pytest pytest-asyncio httpx pytest-cov

echo.
echo ========================================
echo    Running Tests
echo ========================================
echo.

REM Run tests with verbose output
pytest -v

echo.
echo ========================================
echo    Test Summary
echo ========================================
echo.
echo To run specific tests:
echo   pytest backend/test_security.py
echo   pytest backend/test_api.py
echo.
echo To run with coverage:
echo   pytest --cov=backend --cov-report=html
echo.

pause
