#!/bin/bash
# Run browser automation tests

echo "🚀 Starting Crypto Monitor Browser Tests"
echo "========================================"

# Check if server is running
if ! curl -s http://localhost:7860/health > /dev/null 2>&1; then
    echo "⚠️  Warning: Server not responding at http://localhost:7860"
    echo "   Please start the server first:"
    echo "   python production_server.py"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run tests
python browser-testing/test_runner.py

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tests completed successfully!"
else
    echo ""
    echo "❌ Tests failed!"
    exit 1
fi

