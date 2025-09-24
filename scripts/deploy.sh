#!/bin/bash
# Deployment script for Andalus Downloader Backend API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT="${1:-development}"
COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo -e "${BLUE}🚀 Deploying Andalus Downloader Backend API${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Compose file: ${COMPOSE_FILE}${NC}"
echo "=================================="

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p downloads data logs config ssl

# Set permissions
chmod 755 downloads data logs config
if [ -d "ssl" ]; then
    chmod 700 ssl
fi

# Pull latest images (for production)
if [ "$ENVIRONMENT" = "production" ]; then
    echo -e "${YELLOW}📥 Pulling latest images...${NC}"
    docker-compose -f "$COMPOSE_FILE" pull
fi

# Build and start services
echo -e "${YELLOW}🔨 Building and starting services...${NC}"
docker-compose -f "$COMPOSE_FILE" up -d --build

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Check health
echo -e "${YELLOW}🏥 Checking service health...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API service is healthy${NC}"
else
    echo -e "${RED}❌ API service health check failed${NC}"
    echo -e "${YELLOW}📋 Container logs:${NC}"
    docker-compose -f "$COMPOSE_FILE" logs --tail=50 andalus-downloader
    exit 1
fi

# Show running services
echo -e "${BLUE}📊 Running services:${NC}"
docker-compose -f "$COMPOSE_FILE" ps

# Show useful URLs
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📚 Available endpoints:${NC}"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Health Check: http://localhost:8000/health"
echo "  • System Status: http://localhost:8000/api/v1/status"

if [ "$ENVIRONMENT" = "production" ]; then
    echo "  • Nginx Proxy: http://localhost"
    if docker-compose -f "$COMPOSE_FILE" --profile monitoring ps | grep -q prometheus; then
        echo "  • Prometheus: http://localhost:9090"
        echo "  • Grafana: http://localhost:3000 (admin/admin123)"
    fi
fi

echo ""
echo -e "${BLUE}🔧 Management commands:${NC}"
echo "  • View logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "  • Stop services: docker-compose -f $COMPOSE_FILE down"
echo "  • Restart: docker-compose -f $COMPOSE_FILE restart"
echo "  • Update: docker-compose -f $COMPOSE_FILE pull && docker-compose -f $COMPOSE_FILE up -d"

# Show resource usage
echo ""
echo -e "${BLUE}💻 Resource usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
