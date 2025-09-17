#!/bin/bash
# Development run script for Security Modeling Platform

set -e

echo "🚀 Starting Security Modeling Platform (Development)..."

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.dev.yml down

# Build and start services with development configuration
echo "🏗️ Starting development services..."
docker-compose -f docker-compose.dev.yml up --build

echo "✅ Development environment started!"
echo "🌐 Frontend (hot reload): http://localhost:3000"
echo "🔌 Backend API (hot reload): http://localhost:8001"  
echo "🗄️ MongoDB: localhost:27017"

echo ""
echo "📋 Development features:"
echo "  ✅ Hot reload enabled for both frontend and backend"
echo "  ✅ Source code mounted as volumes"
echo "  ✅ Debug logging enabled"