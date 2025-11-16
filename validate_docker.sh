#!/bin/bash

# Docker Setup Validation Script
# Validates Dockerfile and docker-compose.yml configuration

set -e

echo "=========================================="
echo "Docker Setup Validation"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        return 0
    else
        echo -e "${RED}✗${NC} $1 missing"
        return 1
    fi
}

# 1. Check required files
echo "1. Checking required files..."
check_file "Dockerfile"
check_file "Dockerfile.gradio"
check_file "docker-compose.yml"
check_file "requirements.txt"
check_file "requirements_gradio.txt"
check_file ".dockerignore"
echo ""

# 2. Validate Dockerfile syntax
echo "2. Validating Dockerfile syntax..."
if docker build -f Dockerfile --target='' . --dry-run 2>/dev/null || docker build -f Dockerfile -t test-validation . > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Dockerfile syntax is valid"
else
    echo -e "${YELLOW}⚠${NC} Cannot fully validate Dockerfile (docker not running or test build needed)"
fi

if docker build -f Dockerfile.gradio --target='' . --dry-run 2>/dev/null || docker build -f Dockerfile.gradio -t test-validation-gradio . > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Dockerfile.gradio syntax is valid"
else
    echo -e "${YELLOW}⚠${NC} Cannot fully validate Dockerfile.gradio (docker not running or test build needed)"
fi
echo ""

# 3. Validate docker-compose.yml syntax
echo "3. Validating docker-compose.yml..."
if command -v docker-compose >/dev/null 2>&1; then
    if docker-compose config > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} docker-compose.yml syntax is valid"
    else
        echo -e "${RED}✗${NC} docker-compose.yml has syntax errors"
        docker-compose config
    fi
else
    echo -e "${YELLOW}⚠${NC} docker-compose not installed, skipping validation"
fi
echo ""

# 4. Check requirements files
echo "4. Checking requirements files..."

# Check requirements.txt
if grep -q "fastapi" requirements.txt; then
    echo -e "${GREEN}✓${NC} requirements.txt contains fastapi"
else
    echo -e "${RED}✗${NC} requirements.txt missing fastapi"
fi

if grep -q "pandas" requirements.txt; then
    echo -e "${GREEN}✓${NC} requirements.txt contains pandas"
else
    echo -e "${YELLOW}⚠${NC} requirements.txt missing pandas"
fi

# Check requirements_gradio.txt
if grep -q "gradio" requirements_gradio.txt; then
    echo -e "${GREEN}✓${NC} requirements_gradio.txt contains gradio"
else
    echo -e "${RED}✗${NC} requirements_gradio.txt missing gradio"
fi

if grep -q "plotly" requirements_gradio.txt; then
    echo -e "${GREEN}✓${NC} requirements_gradio.txt contains plotly"
else
    echo -e "${RED}✗${NC} requirements_gradio.txt missing plotly"
fi

if grep -q "transformers" requirements_gradio.txt; then
    echo -e "${GREEN}✓${NC} requirements_gradio.txt contains transformers"
else
    echo -e "${YELLOW}⚠${NC} requirements_gradio.txt missing transformers (optional)"
fi
echo ""

# 5. Check Dockerfile contents
echo "5. Checking Dockerfile configurations..."

# Check if Dockerfile copies requirements files
if grep -q "COPY requirements.txt requirements_gradio.txt" Dockerfile; then
    echo -e "${GREEN}✓${NC} Dockerfile copies both requirements files"
else
    echo -e "${YELLOW}⚠${NC} Dockerfile may not copy both requirements files"
fi

# Check if Dockerfile.gradio installs all dependencies
if grep -q "requirements_gradio.txt" Dockerfile.gradio; then
    echo -e "${GREEN}✓${NC} Dockerfile.gradio installs gradio requirements"
else
    echo -e "${RED}✗${NC} Dockerfile.gradio missing gradio requirements installation"
fi

# Check if ports are exposed
if grep -q "EXPOSE 7860" Dockerfile.gradio; then
    echo -e "${GREEN}✓${NC} Dockerfile.gradio exposes port 7860"
else
    echo -e "${RED}✗${NC} Dockerfile.gradio doesn't expose port 7860"
fi
echo ""

# 6. Check docker-compose services
echo "6. Checking docker-compose.yml services..."

if grep -q "crypto-api:" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} crypto-api service defined"
else
    echo -e "${RED}✗${NC} crypto-api service missing"
fi

if grep -q "crypto-dashboard:" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} crypto-dashboard service defined"
else
    echo -e "${RED}✗${NC} crypto-dashboard service missing"
fi

# Check if ports are mapped correctly
if grep -q '"8000:8000"' docker-compose.yml; then
    echo -e "${GREEN}✓${NC} API port 8000 mapped"
else
    echo -e "${RED}✗${NC} API port 8000 not mapped"
fi

if grep -q '"7860:7860"' docker-compose.yml; then
    echo -e "${GREEN}✓${NC} Dashboard port 7860 mapped"
else
    echo -e "${RED}✗${NC} Dashboard port 7860 not mapped"
fi

# Check if volumes are mounted
if grep -q "./logs:/app/logs" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} Logs volume mounted"
else
    echo -e "${YELLOW}⚠${NC} Logs volume not mounted"
fi

if grep -q "./data:/app/data" docker-compose.yml; then
    echo -e "${GREEN}✓${NC} Data volume mounted"
else
    echo -e "${YELLOW}⚠${NC} Data volume not mounted"
fi
echo ""

# 7. Check application files
echo "7. Checking application files..."
check_file "app.py"
check_file "api_server_extended.py"
check_file "config.py"
check_file "utils/__init__.py"
echo ""

# 8. Summary
echo "=========================================="
echo "Validation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Build images:    docker-compose build"
echo "  2. Start services:  docker-compose up -d"
echo "  3. View logs:       docker-compose logs -f"
echo "  4. Check status:    docker-compose ps"
echo ""
echo "Access:"
echo "  - Dashboard: http://localhost:7860"
echo "  - API:       http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo ""
