#!/bin/bash
# Quick Docker deployment script for Crypto API Monitor

set -e

echo "🐳 Building Docker image for Crypto API Monitor..."
docker build -t crypto-api-monitor:latest .

echo ""
echo "✅ Build complete!"
echo ""
echo "🚀 Starting container..."
docker run -d \
  --name crypto-monitor \
  -p 7860:7860 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  crypto-api-monitor:latest

echo ""
echo "✅ Container started successfully!"
echo ""
echo "📊 Dashboard: http://localhost:7860"
echo "📚 API Docs: http://localhost:7860/docs"
echo "🔍 Health Check: http://localhost:7860/health"
echo ""
echo "📝 View logs:"
echo "   docker logs -f crypto-monitor"
echo ""
echo "🛑 Stop container:"
echo "   docker stop crypto-monitor && docker rm crypto-monitor"
