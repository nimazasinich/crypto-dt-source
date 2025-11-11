#!/bin/bash
# ============================================================================
# Quick Start Script for Crypto API Monitoring System
# ============================================================================

set -e

echo "🚀 Starting Crypto API Monitoring System..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys!"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose found!"
echo ""

# Build and start
echo "📦 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for application to start..."
sleep 10

# Check health
echo "🔍 Checking application health..."
if curl -f http://localhost:7860/api/health > /dev/null 2>&1; then
    echo "✅ Application is healthy!"
else
    echo "⚠️  Application might not be ready yet. Check logs with: docker-compose logs -f"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Crypto API Monitor is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Dashboard:  http://localhost:7860"
echo "📊 API Docs:   http://localhost:7860/docs"
echo "🔧 API Status: http://localhost:7860/api/status"
echo ""
echo "📋 Useful commands:"
echo "   docker-compose logs -f         # View logs"
echo "   docker-compose ps              # Check status"
echo "   docker-compose down            # Stop services"
echo "   docker-compose restart         # Restart services"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
