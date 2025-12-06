#!/bin/bash
# Setup script for CryptoBERT model authentication
# This script configures the HF_TOKEN environment variable for accessing authenticated Hugging Face models

echo "========================================="
echo "CryptoBERT Model Authentication Setup"
echo "========================================="
echo ""

# Default token (can be overridden)
DEFAULT_TOKEN="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"

# Check if HF_TOKEN is already set
if [ -n "$HF_TOKEN" ]; then
    echo "✓ HF_TOKEN is already set in environment"
    echo "  Current value: ${HF_TOKEN:0:10}...${HF_TOKEN: -5}"
else
    echo "⚠ HF_TOKEN not found in environment"
    echo ""
    echo "Setting HF_TOKEN to default value..."
    export HF_TOKEN="$DEFAULT_TOKEN"
    echo "✓ HF_TOKEN set for current session"
fi

echo ""
echo "========================================="
echo "Model Information"
echo "========================================="
echo "Model: ElKulako/CryptoBERT"
echo "Model ID: hf_model_elkulako_cryptobert"
echo "Status: CONDITIONALLY_AVAILABLE (requires authentication)"
echo "Task: fill-mask (masked language model)"
echo "Use case: Cryptocurrency-specific sentiment analysis"
echo ""

echo "========================================="
echo "Usage Instructions"
echo "========================================="
echo ""
echo "1. For current session only:"
echo "   export HF_TOKEN='$DEFAULT_TOKEN'"
echo ""
echo "2. For persistent setup, add to ~/.bashrc or ~/.zshrc:"
echo "   echo 'export HF_TOKEN=\"$DEFAULT_TOKEN\"' >> ~/.bashrc"
echo "   source ~/.bashrc"
echo ""
echo "3. For Python scripts, the token is automatically loaded from:"
echo "   - Environment variable HF_TOKEN"
echo "   - Or uses default value in config.py"
echo ""
echo "4. Test the setup:"
echo "   python3 -c \"import ai_models; print(ai_models.get_model_info())\""
echo ""

echo "========================================="
echo "API Usage Example"
echo "========================================="
echo ""
echo "Python usage:"
echo ""
cat << 'EOF'
import ai_models

# Initialize all models (including CryptoBERT)
result = ai_models.initialize_models()
print(f"Models loaded: {result['models']}")

# Use CryptoBERT for crypto sentiment analysis
text = "Bitcoin shows strong bullish momentum with increasing adoption"
sentiment = ai_models.analyze_crypto_sentiment(text)
print(f"Sentiment: {sentiment['label']}")
print(f"Confidence: {sentiment['score']}")
print(f"Predictions: {sentiment.get('predictions', [])}")
EOF

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
