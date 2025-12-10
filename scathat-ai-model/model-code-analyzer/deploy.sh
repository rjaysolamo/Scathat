#!/bin/bash

# Model Code Analyzer Deployment Script
set -e

SERVICE_NAME="scathat-code-analyzer"
PORT=8002
IMAGE_NAME="scathat-code-analyzer"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Deploying Scathat Code Analyzer Service${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Stop and remove existing container if it exists
if docker ps -a --filter "name=$SERVICE_NAME" | grep -q "$SERVICE_NAME"; then
    echo -e "${YELLOW}Stopping existing container...${NC}"
    docker stop $SERVICE_NAME > /dev/null 2>&1 || true
    docker rm $SERVICE_NAME > /dev/null 2>&1 || true
    echo -e "${GREEN}✓ Removed existing container${NC}"
fi

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t $IMAGE_NAME .

echo -e "${GREEN}✓ Docker image built successfully${NC}"

# Run the container
echo -e "${YELLOW}Starting container...${NC}"
docker run -d \
    --name $SERVICE_NAME \
    --network host \
    -p $PORT:$PORT \
    -e MODEL_PATH="./fine_tuned_model" \
    -e LOG_LEVEL="INFO" \
    $IMAGE_NAME

echo -e "${GREEN}✓ Container started successfully${NC}"

# Wait a moment for the service to start
sleep 5

# Health check
echo -e "${YELLOW}Performing health check...${NC}"
if docker exec $SERVICE_NAME curl -f http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed. Checking logs...${NC}"
    docker logs $SERVICE_NAME
    exit 1
fi

echo -e "${GREEN}🎉 Scathat Code Analyzer deployed successfully!${NC}"
echo -e "${YELLOW}📊 Service endpoints:${NC}"
echo -e "   Health: http://localhost:$PORT/health"
echo -e "   Analyze: http://localhost:$PORT/analyze"
echo -e "   Info: http://localhost:$PORT/info"
echo -e ""
echo -e "${YELLOW}📋 To check logs:${NC}"
echo -e "   docker logs $SERVICE_NAME"
echo -e ""
echo -e "${YELLOW}🛑 To stop the service:${NC}"
echo -e "   docker stop $SERVICE_NAME"