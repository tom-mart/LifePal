#!/bin/bash

# LifePal Deployment Script

set -e  # Exit on error

echo "🚀 Starting LifePal deployment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    exit 1
fi

# Generate SSL certificates if they don't exist
if [ ! -f ssl/localhost.crt ] || [ ! -f ssl/localhost.key ]; then
    echo "🔐 Generating SSL certificates..."
    chmod +x generate-ssl.sh
    ./generate-ssl.sh
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose down

# Build and start services
echo "🏗️  Building Docker images..."
sudo docker-compose build --no-cache

echo "🚀 Starting services..."
sudo docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
sudo docker-compose ps

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📍 Access points:"
echo "   - Frontend: http://192.168.1.229:8082"
echo "   - Frontend (HTTPS): https://192.168.1.229:8443"
echo "   - Backend API: http://192.168.1.229:8082/api"
echo "   - Django Admin: http://192.168.1.229:8082/admin"
echo ""
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop services with: docker-compose down"
