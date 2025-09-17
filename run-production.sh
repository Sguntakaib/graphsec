#!/bin/bash
# Production run script for Security Modeling Platform

set -e

echo "🚀 Starting Security Modeling Platform (Production)..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Pull latest MongoDB image
echo "📦 Pulling MongoDB image..."
docker pull mongo:7.0

# Build and start services
echo "🏗️ Building and starting services..."
docker-compose up --build -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Check logs for any errors
echo "📝 Recent logs:"
docker-compose logs --tail=10

echo "✅ Security Modeling Platform is running!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8001"
echo "🗄️ MongoDB: localhost:27017"

echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart: docker-compose restart"