#!/bin/bash
# Deployment Verification Script
# Run this script to verify the deployment is ready

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🔍 DEPLOYMENT VERIFICATION SCRIPT                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0

# Check 1: Required files exist
echo "📋 Check 1: Required files..."
for file in requirements.txt Dockerfile api_server_extended.py provider_fetch_helper.py database.py; do
    if [ -f "$file" ]; then
        echo "  ✅ $file exists"
    else
        echo "  ❌ $file missing"
        ((ERRORS++))
    fi
done
echo ""

# Check 2: Dockerfile configuration
echo "🐳 Check 2: Dockerfile configuration..."
if grep -q "USE_MOCK_DATA=false" Dockerfile; then
    echo "  ✅ USE_MOCK_DATA environment variable set"
else
    echo "  ❌ USE_MOCK_DATA not found in Dockerfile"
    ((ERRORS++))
fi

if grep -q "mkdir -p logs data exports backups" Dockerfile; then
    echo "  ✅ Directory creation configured"
else
    echo "  ❌ Directory creation missing"
    ((ERRORS++))
fi

if grep -q "uvicorn api_server_extended:app" Dockerfile; then
    echo "  ✅ Uvicorn startup command configured"
else
    echo "  ❌ Uvicorn startup command missing"
    ((ERRORS++))
fi
echo ""

# Check 3: Requirements.txt dependencies
echo "📦 Check 3: Required dependencies..."
for dep in fastapi uvicorn pydantic sqlalchemy aiohttp; do
    if grep -q "$dep" requirements.txt; then
        echo "  ✅ $dep found in requirements.txt"
    else
        echo "  ❌ $dep missing from requirements.txt"
        ((ERRORS++))
    fi
done
echo ""

# Check 4: USE_MOCK_DATA implementation
echo "🔧 Check 4: USE_MOCK_DATA flag implementation..."
if grep -q 'USE_MOCK_DATA = os.getenv("USE_MOCK_DATA"' api_server_extended.py; then
    echo "  ✅ USE_MOCK_DATA flag implemented"
else
    echo "  ❌ USE_MOCK_DATA flag not found"
    ((ERRORS++))
fi
echo ""

# Check 5: Real data collectors imported
echo "🌐 Check 5: Real data collector imports..."
if grep -q "from collectors.sentiment import get_fear_greed_index" api_server_extended.py; then
    echo "  ✅ Sentiment collector imported"
else
    echo "  ❌ Sentiment collector import missing"
    ((ERRORS++))
fi

if grep -q "from collectors.market_data import get_coingecko_simple_price" api_server_extended.py; then
    echo "  ✅ Market data collector imported"
else
    echo "  ❌ Market data collector import missing"
    ((ERRORS++))
fi

if grep -q "from database import get_database" api_server_extended.py; then
    echo "  ✅ Database import found"
else
    echo "  ❌ Database import missing"
    ((ERRORS++))
fi
echo ""

# Check 6: Mock data removed from endpoints
echo "🚫 Check 6: Mock data handling..."
MOCK_COUNT=$(grep -c "if USE_MOCK_DATA:" api_server_extended.py || echo "0")
if [ "$MOCK_COUNT" -ge 5 ]; then
    echo "  ✅ USE_MOCK_DATA checks found in $MOCK_COUNT locations"
else
    echo "  ⚠️  USE_MOCK_DATA checks found in only $MOCK_COUNT locations (expected 5+)"
    ((ERRORS++))
fi
echo ""

# Check 7: Database integration
echo "💾 Check 7: Database integration..."
if grep -q "db.save_price" api_server_extended.py; then
    echo "  ✅ Database save_price integration found"
else
    echo "  ❌ Database save_price integration missing"
    ((ERRORS++))
fi

if grep -q "db.get_price_history" api_server_extended.py; then
    echo "  ✅ Database get_price_history integration found"
else
    echo "  ❌ Database get_price_history integration missing"
    ((ERRORS++))
fi
echo ""

# Check 8: Error handling for unimplemented endpoints
echo "⚠️  Check 8: Proper error codes for unimplemented endpoints..."
if grep -q "status_code=503" api_server_extended.py; then
    echo "  ✅ HTTP 503 error handling found"
else
    echo "  ❌ HTTP 503 error handling missing"
    ((ERRORS++))
fi

if grep -q "status_code=501" api_server_extended.py; then
    echo "  ✅ HTTP 501 error handling found"
else
    echo "  ❌ HTTP 501 error handling missing"
    ((ERRORS++))
fi
echo ""

# Check 9: Python syntax
echo "🐍 Check 9: Python syntax validation..."
if python3 -m py_compile api_server_extended.py 2>/dev/null; then
    echo "  ✅ api_server_extended.py syntax valid"
else
    echo "  ❌ api_server_extended.py syntax errors"
    ((ERRORS++))
fi

if python3 -m py_compile provider_fetch_helper.py 2>/dev/null; then
    echo "  ✅ provider_fetch_helper.py syntax valid"
else
    echo "  ❌ provider_fetch_helper.py syntax errors"
    ((ERRORS++))
fi
echo ""

# Check 10: Documentation
echo "📄 Check 10: Documentation..."
if [ -f "DEPLOYMENT_INSTRUCTIONS.md" ]; then
    echo "  ✅ DEPLOYMENT_INSTRUCTIONS.md exists"
else
    echo "  ⚠️  DEPLOYMENT_INSTRUCTIONS.md missing (recommended)"
fi

if [ -f "AUDIT_COMPLETION_REPORT.md" ]; then
    echo "  ✅ AUDIT_COMPLETION_REPORT.md exists"
else
    echo "  ⚠️  AUDIT_COMPLETION_REPORT.md missing (recommended)"
fi
echo ""

# Final verdict
echo "═══════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo "║  ✅ ALL CHECKS PASSED                                    ║"
    echo "║  STATUS: READY FOR HUGGINGFACE DEPLOYMENT ✅            ║"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. docker build -t crypto-monitor ."
    echo "   2. docker run -p 7860:7860 crypto-monitor"
    echo "   3. Test: curl http://localhost:7860/health"
    echo "   4. Deploy to HuggingFace Spaces"
    echo ""
    exit 0
else
    echo "║  ❌ FOUND $ERRORS ERROR(S)                                  ║"
    echo "║  STATUS: NOT READY FOR DEPLOYMENT ❌                    ║"
    echo "═══════════════════════════════════════════════════════════"
    echo ""
    echo "⚠️  Please fix the errors above before deploying."
    echo ""
    exit 1
fi
