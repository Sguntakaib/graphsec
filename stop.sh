#!/bin/bash
# Stop script for Security Modeling Platform

set -e

echo "🛑 Stopping Security Modeling Platform..."

# Stop production containers
if [ -f "docker-compose.yml" ]; then
    echo "Stopping production services..."
    docker-compose down
fi

# Stop development containers
if [ -f "docker-compose.dev.yml" ]; then
    echo "Stopping development services..."
    docker-compose -f docker-compose.dev.yml down
fi

# Optional: Remove volumes (uncomment if you want to clean data)
# echo "🗑️ Removing data volumes..."
# docker volume rm $(docker volume ls -q | grep security-platform) 2>/dev/null || true

echo "✅ All services stopped!"

# Show remaining containers (if any)
echo "📊 Remaining containers:"
docker ps | grep security-platform || echo "No security-platform containers running"