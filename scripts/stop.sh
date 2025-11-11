#!/bin/bash
# ============================================================================
# Stop Script for Crypto API Monitoring System
# ============================================================================

echo "🛑 Stopping Crypto API Monitoring System..."
echo ""

docker-compose down

echo ""
echo "✅ Services stopped successfully!"
echo ""
echo "To remove all data (CAUTION), run:"
echo "   docker-compose down -v"
