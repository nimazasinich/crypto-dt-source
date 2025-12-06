@echo off
REM Run browser automation tests on Windows

echo ========================================
echo Starting Crypto Monitor Browser Tests
echo ========================================
echo.

REM Check if server is running
curl -s http://localhost:7860/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Server not responding at http://localhost:7860
    echo Please start the server first:
    echo    python production_server.py
    echo.
    set /p CONTINUE="Continue anyway? (y/N): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

REM Run tests
python browser-testing\test_runner.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo Tests completed successfully!
) else (
    echo.
    echo Tests failed!
    exit /b 1
)

