#!/bin/bash
# ============================================================================
# Deploy to Hugging Face Spaces
# ============================================================================

set -e

echo "🤗 Deploying to Hugging Face Spaces..."
echo ""

# Check if huggingface-cli is installed
if ! command -v huggingface-cli &> /dev/null; then
    echo "❌ huggingface-cli not found. Installing..."
    pip install --upgrade huggingface_hub
fi

# Login check
echo "Checking Hugging Face authentication..."
if ! huggingface-cli whoami > /dev/null 2>&1; then
    echo "Please login to Hugging Face:"
    huggingface-cli login
fi

# Get Space name
read -p "Enter your Hugging Face username: " HF_USERNAME
read -p "Enter Space name (default: crypto-monitor): " SPACE_NAME
SPACE_NAME=${SPACE_NAME:-crypto-monitor}

echo ""
echo "📋 Configuration:"
echo "   Username: $HF_USERNAME"
echo "   Space:    $SPACE_NAME"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Ensure README has HF metadata
echo "📝 Preparing README for Hugging Face..."
if [ -f README_HUGGINGFACE.md ]; then
    cp README_HUGGINGFACE.md README.md
    echo "✅ README updated with HF metadata"
fi

# Add HF remote if not exists
if ! git remote get-url hf > /dev/null 2>&1; then
    git remote add hf https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME
    echo "✅ Added Hugging Face remote"
fi

# Commit changes
echo "📦 Committing changes..."
git add .
git commit -m "Deploy to Hugging Face Spaces" || echo "No changes to commit"

# Push to HF
echo "🚀 Pushing to Hugging Face..."
git push hf main --force

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Deployment complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Your Space: https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo ""
echo "⚠️  Remember to add API keys in Space Settings → Repository Secrets:"
echo "   - ETHERSCAN_KEY_1"
echo "   - COINMARKETCAP_KEY_1"
echo "   - NEWSAPI_KEY"
echo ""
