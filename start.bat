@echo off
chcp 65001 > nul
title Crypto Monitor ULTIMATE - Real APIs

echo ========================================
echo   🚀 Crypto Monitor ULTIMATE
echo   Real-time Data from 100+ Free APIs
echo ========================================
echo.

python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    pause
    exit /b 1
)

echo ✅ Python found
echo.

if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

echo 🔧 Activating environment...
call venv\Scripts\activate.bat

echo 📥 Installing packages...
pip install -q -r requirements.txt

echo.
echo ========================================
echo   🎯 Starting Real-time Server...
echo ========================================
echo.
echo 📊 Dashboard: http://localhost:8000/dashboard
echo 📡 API Docs: http://localhost:8000/docs
echo.
echo 💡 Real APIs:
echo    ✓ CoinGecko - Market Data
echo    ✓ CoinCap - Price Data
echo    ✓ Binance - Exchange Data
echo    ✓ Fear & Greed Index
echo    ✓ DeFi Llama - TVL Data
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python app.py

pause
