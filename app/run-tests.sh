#!/bin/bash
# Script to run tests in Docker

set -e

echo "🧪 Running Digital Lockbox API Tests in Docker..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
TEST_PATH="${1:-}"
EXTRA_ARGS="${@:2}"

# Detect docker compose command (v1 vs v2)
if command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE="docker compose"
else
    echo "Error: Neither 'docker-compose' nor 'docker compose' is available"
    exit 1
fi

# Build and run tests
echo -e "${YELLOW}Building test container...${NC}"
$COMPOSE -f docker-compose.yml --profile test build api_test

echo ""
echo -e "${YELLOW}Starting database...${NC}"
$COMPOSE up -d db

echo ""
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
sleep 5

echo ""
echo -e "${YELLOW}Running migrations...${NC}"
$COMPOSE --profile test run --rm api_test sh -c "cd /app/authentication && python manage.py migrate --noinput"

echo ""
echo -e "${GREEN}Running tests...${NC}"
if [ -z "$TEST_PATH" ]; then
    # Run all tests
    $COMPOSE --profile test run --rm api_test sh -c "cd /app/authentication && pytest -n auto -v --cov=authentication --cov-config=../.coveragerc --cov-report=html --cov-report=term-missing $EXTRA_ARGS"
else
    # Run specific test path
    $COMPOSE --profile test run --rm api_test sh -c "cd /app/authentication && pytest -n auto -v $TEST_PATH $EXTRA_ARGS"
fi

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Tests passed!${NC}"
else
    echo -e "${YELLOW}❌ Tests failed!${NC}"
fi

echo ""
echo "Coverage report available at: digitalockbox_api/authentication/htmlcov/index.html"

# Cleanup
echo ""
echo -e "${YELLOW}Stopping containers...${NC}"
$COMPOSE down

exit $TEST_EXIT_CODE
