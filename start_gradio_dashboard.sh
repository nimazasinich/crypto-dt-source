#!/bin/bash
#
# Start Gradio Dashboard for Crypto Data Sources
#

echo "🚀 Starting Gradio Dashboard..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if needed
if ! python -c "import gradio" 2>/dev/null; then
    echo "📥 Installing Gradio and dependencies..."
    pip install -q -r requirements_gradio.txt
fi

echo "✅ All dependencies installed"
echo ""
echo "🌐 Starting dashboard on http://localhost:7861"
echo "📊 Dashboard will monitor:"
echo "   - FastAPI Backend (http://localhost:7860)"
echo "   - HF Data Engine (http://localhost:8000)"
echo "   - 200+ Crypto Data Sources"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the dashboard
python gradio_ultimate_dashboard.py
