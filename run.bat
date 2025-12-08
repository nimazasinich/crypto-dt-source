@echo off
REM FastAPI Server Startup Script for Windows
echo ========================================
echo Starting FastAPI Server
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if uvicorn is installed
python -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo ERROR: uvicorn is not installed
    echo Installing uvicorn...
    pip install uvicorn[standard]
    if errorlevel 1 (
        echo ERROR: Failed to install uvicorn
        pause
        exit /b 1
    )
)

REM Set default port if not set
if "%PORT%"=="" set PORT=7860
if "%HOST%"=="" set HOST=0.0.0.0

echo Starting server on %HOST%:%PORT%...
echo.
echo Access points:
echo   - Dashboard: http://localhost:%PORT%/
echo   - API Docs: http://localhost:%PORT%/docs
echo   - System Monitor: http://localhost:%PORT%/system-monitor
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run the server
python main.py

pause

