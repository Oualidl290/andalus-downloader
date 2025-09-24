#!/bin/bash
# Docker build script for Andalus Downloader Backend API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="andalus-downloader"
TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"

echo -e "${BLUE}🐳 Building Andalus Downloader Docker Image${NC}"
echo -e "${BLUE}Image: ${FULL_IMAGE_NAME}${NC}"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Build the Docker image
echo -e "${YELLOW}📦 Building Docker image...${NC}"
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
    
    # Show image details
    echo -e "${BLUE}📊 Image Details:${NC}"
    docker images "${IMAGE_NAME}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    # Optional: Run a quick test
    echo -e "${YELLOW}🧪 Running quick health check...${NC}"
    CONTAINER_ID=$(docker run -d -p 8001:8000 "${FULL_IMAGE_NAME}")
    
    # Wait for container to start
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health check passed!${NC}"
    else
        echo -e "${RED}❌ Health check failed${NC}"
    fi
    
    # Clean up test container
    docker stop "${CONTAINER_ID}" > /dev/null
    docker rm "${CONTAINER_ID}" > /dev/null
    
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo -e "${BLUE}To run the container:${NC}"
    echo "  docker run -p 8000:8000 ${FULL_IMAGE_NAME}"
    echo -e "${BLUE}Or use docker-compose:${NC}"
    echo "  docker-compose up -d"
    
else
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi
