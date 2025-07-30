@echo off
REM Network Automation Dashboard Startup Script
REM This script starts the network automation dashboard

echo ====================================
echo Network Automation Dashboard
echo Starting Application...
echo ====================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found
    echo Please run setup.py first to initialize the project
    pause
    exit /b 1
)

REM Activate virtual environment and start application
echo Activating Python virtual environment...
call .venv\Scripts\activate.bat

echo Starting Flask application...
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

REM Start the application
.venv\Scripts\python.exe main.py

echo.
echo Application stopped.
pause
