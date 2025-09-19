#!/bin/bash

# Production deployment script for HDFS system
set -e

echo "🚀 Deploying HDFS System to Production..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your production settings!"
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/datanode1 data/datanode2

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Health check
echo "🔍 Performing health checks..."
if curl -f http://localhost:5050/api/v1/stats > /dev/null 2>&1; then
    echo "✅ NameNode is healthy"
else
    echo "❌ NameNode health check failed"
fi

if curl -f http://localhost:5001/api/v1/info > /dev/null 2>&1; then
    echo "✅ DataNode 1 is healthy"
else
    echo "❌ DataNode 1 health check failed"
fi

if curl -f http://localhost:5002/api/v1/info > /dev/null 2>&1; then
    echo "✅ DataNode 2 is healthy"
else
    echo "❌ DataNode 2 health check failed"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "🌐 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   NameNode API: http://localhost:5050"
echo "   DataNode 1: http://localhost:5001"
echo "   DataNode 2: http://localhost:5002"
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart"
