#!/bin/bash

# Instant-RAG Quick Start Script

echo "🚀 Starting Instant-RAG Platform..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating data directories..."
mkdir -p data identity

# Build and start the service
echo "🔨 Building and starting services..."
docker compose up --build -d

# Wait for service to be ready
echo "⏳ Waiting for service to start..."
sleep 5

# Check if service is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Service is running!"
    echo ""
    echo "📍 API available at: http://localhost:8000"
    echo "📚 API docs at: http://localhost:8000/docs"
    echo ""
    echo "🔑 To create an agent token, run:"
    echo "   docker compose exec app python -c \"from identity.passport import passport; print('Token:', passport.issue('my-agent'))\""
    echo ""
    echo "📊 To view logs:"
    echo "   docker compose logs -f"
    echo ""
    echo "🛑 To stop:"
    echo "   docker compose down"
else
    echo "❌ Service failed to start. Check logs with: docker compose logs"
    exit 1
fi
