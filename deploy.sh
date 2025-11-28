#!/bin/bash

echo "Starting MedAssist Deployment..."

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker and try again"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo "Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Build and start the application
echo "Building MedAssist container..."
docker-compose build

echo "Starting MedAssist services..."
docker-compose up -d

echo "Waiting for services to start..."
sleep 10

# Check if services are running
docker-compose ps

echo ""
echo "========================================"
echo "MedAssist Deployment Complete!"
echo "========================================"
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "Health: http://localhost:8000/health"
echo "========================================"
echo ""
echo "Press Enter to view logs..."
read
docker-compose logs -f