#!/bin/bash
# Hugging Face Spaces Deployment Helper Script

echo "🚀 Crypto Intelligence Hub - HF Spaces Deployment"
echo "=================================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Ask for UI mode
echo "Choose UI mode for Hugging Face Spaces:"
echo "1) Gradio UI (Recommended - Interactive dashboard)"
echo "2) FastAPI + HTML (REST API with HTML frontend)"
echo ""
read -p "Enter choice (1 or 2): " ui_choice

if [ "$ui_choice" = "1" ]; then
    echo "✅ Setting up Gradio UI mode..."
    sed -i 's/ENV USE_FASTAPI_HTML=true/ENV USE_FASTAPI_HTML=false/' Dockerfile
    sed -i 's/ENV USE_GRADIO=false/ENV USE_GRADIO=true/' Dockerfile
    echo "✅ Dockerfile updated for Gradio mode"
elif [ "$ui_choice" = "2" ]; then
    echo "✅ Setting up FastAPI + HTML mode..."
    sed -i 's/ENV USE_FASTAPI_HTML=false/ENV USE_FASTAPI_HTML=true/' Dockerfile
    sed -i 's/ENV USE_GRADIO=true/ENV USE_GRADIO=false/' Dockerfile
    echo "✅ Dockerfile updated for FastAPI mode"
else
    echo "❌ Invalid choice. Keeping current settings."
fi

echo ""
echo "📝 Next steps:"
echo "1. Create a new Space at: https://huggingface.co/new-space"
echo "   - Choose 'Docker' as SDK"
echo "   - Choose your preferred hardware tier"
echo ""
echo "2. Clone your new Space:"
echo "   git clone https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME"
echo ""
echo "3. Copy files to the Space directory:"
echo "   cp -r * /path/to/your/space/"
echo ""
echo "4. Push to HF Spaces:"
echo "   cd /path/to/your/space/"
echo "   git add ."
echo "   git commit -m 'Initial deployment'"
echo "   git push"
echo ""
echo "✅ Your app is ready to deploy!"
