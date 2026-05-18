#!/bin/bash
# Run all Muralis tests

set -e

echo "🧪 Running Muralis Test Suite"
echo "============================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠️  Virtual environment not activated${NC}"
    echo "Activating venv..."
    source venv/bin/activate
fi

# Install test dependencies if not already
echo "📦 Installing test dependencies..."
pip install pytest pytest-cov pytest-mock --quiet

# Run unit tests
echo ""
echo -e "${GREEN}📋 Running Unit Tests...${NC}"
pytest tests/unit/ -v --tb=short

# Run integration tests if they exist
if [ -d "tests/integration" ] && [ "$(ls -A tests/integration)" ]; then
    echo ""
    echo -e "${GREEN}🔗 Running Integration Tests...${NC}"
    pytest tests/integration/ -v --tb=short
fi

# Run with coverage
echo ""
echo -e "${GREEN}📊 Running Tests with Coverage...${NC}"
pytest tests/ --cov=muralis --cov-report=term --cov-report=html --cov-report=xml

# Display coverage summary
echo ""
echo -e "${GREEN}✅ Test Suite Complete!${NC}"
echo ""
echo "Coverage report saved to: htmlcov/index.html"
echo "XML report saved to: coverage.xml"

# Check coverage threshold
COVERAGE=$(pytest --cov=muralis --cov-report=term --quiet 2>&1 | grep TOTAL | awk '{print $4}' | sed 's/%//')
if [ -n "$COVERAGE" ]; then
    echo ""
    echo "Total coverage: ${COVERAGE}%"
    if (( $(echo "$COVERAGE < 70" | bc -l) )); then
        echo -e "${RED}⚠️  Coverage below 70%${NC}"
    else
        echo -e "${GREEN}✓ Coverage meets threshold${NC}"
    fi
fi
