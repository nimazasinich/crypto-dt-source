#!/bin/bash
###############################################################################
# Crypto Data Bank Startup Script
# راه‌اندازی بانک اطلاعاتی رمزارز
###############################################################################

echo "========================================================================"
echo "🏦 Crypto Data Bank - Starting..."
echo "========================================================================"

# Create data directory if it doesn't exist
mkdir -p data

# Check if virtual environment exists
if [ ! -d "venv_crypto_bank" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv_crypto_bank
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv_crypto_bank/bin/activate

# Install/upgrade requirements
echo "📥 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r crypto_data_bank/requirements.txt > /dev/null 2>&1

# Check installation
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed"
echo ""

# Start the API Gateway
echo "========================================================================"
echo "🚀 Starting Crypto Data Bank API Gateway..."
echo "========================================================================"
echo ""
echo "📍 API URL: http://localhost:8888"
echo "📖 Documentation: http://localhost:8888/docs"
echo "📊 API Info: http://localhost:8888"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================================================"
echo ""

# Run the API Gateway
cd crypto_data_bank
python api_gateway.py
