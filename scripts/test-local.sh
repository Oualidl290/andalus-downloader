#!/bin/bash
# Local testing script for Andalus Downloader Backend API (Linux/macOS)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐳 Andalus Downloader - Local Development & Testing${NC}"
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Build and start development environment
echo -e "${YELLOW}🔨 Building development environment...${NC}"
docker-compose -f docker-compose.test.yml build andalus-dev

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to build development environment${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Development environment built successfully${NC}"

# Start the development server
echo -e "${YELLOW}🚀 Starting development server...${NC}"
docker-compose -f docker-compose.test.yml up -d andalus-dev

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start development server${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Development server started${NC}"

# Wait for server to be ready
echo -e "${YELLOW}⏳ Waiting for server to be ready...${NC}"
sleep 15

# Test if server is responding
echo -e "${YELLOW}🧪 Testing server health...${NC}"
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is healthy and responding${NC}"
        break
    fi
    echo "Attempt $i/10 - Server not ready yet..."
    sleep 3
    
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Server failed to start properly${NC}"
        echo -e "${YELLOW}📋 Checking server logs:${NC}"
        docker-compose -f docker-compose.test.yml logs --tail=20 andalus-dev
        exit 1
    fi
done

# Run endpoint tests
echo -e "${YELLOW}🧪 Running endpoint tests...${NC}"
docker-compose -f docker-compose.test.yml run --rm andalus-test

# Show server status
echo -e "${BLUE}📊 Server Status:${NC}"
docker-compose -f docker-compose.test.yml ps

echo -e "${BLUE}🌐 Available endpoints:${NC}"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • System Status: http://localhost:8000/api/v1/status"
echo "  • WebSocket: ws://localhost:8000/ws/downloads"

echo -e "${BLUE}🔧 Management commands:${NC}"
echo "  • View logs: docker-compose -f docker-compose.test.yml logs -f andalus-dev"
echo "  • Stop server: docker-compose -f docker-compose.test.yml down"
echo "  • Shell access: docker-compose -f docker-compose.test.yml exec andalus-dev bash"
echo "  • Run tests: docker-compose -f docker-compose.test.yml run --rm andalus-test"

echo -e "${GREEN}🎉 Local testing environment is ready!${NC}"
