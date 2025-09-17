#!/bin/bash
# Build script for Security Modeling Platform

set -e

echo "🚀 Building Security Modeling Platform..."

# Build all Docker images
echo "📦 Building backend image..."
docker build -t security-platform-backend ./backend

echo "📦 Building frontend image..."
docker build -t security-platform-frontend ./frontend

echo "✅ Build completed successfully!"

echo "🐳 Available images:"
docker images | grep security-platform