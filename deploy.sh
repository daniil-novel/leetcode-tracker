#!/bin/bash

# Production deployment script for LeetCode Tracker
# Updated at 2025-12-30
# Stop on error
set -e

echo "🚀 Starting production deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "   Please create .env file from .env.example"
    echo "   Command: cp .env.example .env"
    exit 1
fi

echo "✅ .env file found"

# 1. Stop systemd service if it exists and is running
if systemctl is-active --quiet leetcode-tracker.service 2>/dev/null; then
    echo "🛑 Stopping legacy systemd service..."
    sudo systemctl stop leetcode-tracker.service
    sudo systemctl disable leetcode-tracker.service
    echo "✅ Systemd service stopped and disabled"
fi

# 2. Pull latest changes
echo "📥 Pulling latest code from repository..."
if ! git pull; then
    echo "❌ ERROR: Failed to pull latest changes"
    exit 1
fi
echo "✅ Code updated successfully"

# 3. Determine Docker command
echo "🔍 Checking Docker environment..."
if command -v docker-compose >/dev/null 2>&1; then
    echo "✅ Found 'docker-compose' (standalone)"
    DOCKER_CMD="docker-compose"
else
    echo "⚠️  'docker-compose' not found, trying 'docker compose' (plugin)"
    DOCKER_CMD="docker compose"
fi

# Verify Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ ERROR: Docker is not running"
    exit 1
fi
echo "✅ Docker is running"

# 4. Stop and remove old containers to avoid ContainerConfig errors
echo "🧹 Cleaning up old containers..."
$DOCKER_CMD down --remove-orphans || true

# 4.1. Force remove any remaining containers from this project
echo "🧹 Force removing any remaining containers..."
docker ps -a --filter "name=leetcode" --filter "name=prometheus" --filter "name=grafana" --filter "name=cadvisor" --filter "name=node_exporter" -q | xargs -r docker rm -f || true

# 4.2. Wait a moment for ports to be released
echo "⏳ Waiting for ports to be released..."
sleep 2

# 5. Build and start containers
echo "🐳 Building and starting containers using: $DOCKER_CMD"
if ! $DOCKER_CMD up -d --build; then
    echo "❌ ERROR: Failed to build and start containers"
    exit 1
fi
echo "✅ Containers started successfully"

# 6. Run migrations
echo "🔄 Running database migrations..."
echo "⏳ Waiting for database to be ready..."
sleep 5

if ! $DOCKER_CMD exec -T app uv run alembic upgrade head; then
    echo "❌ ERROR: Database migrations failed"
    echo "📋 Container logs:"
    $DOCKER_CMD logs app --tail 50
    exit 1
fi
echo "✅ Database migrations completed successfully"

# 7. Display container status
echo ""
echo "📊 Container status:"
$DOCKER_CMD ps

# 8. Check if containers are healthy
echo ""
echo "🔍 Checking container health..."
UNHEALTHY_CONTAINERS=$($DOCKER_CMD ps --filter "health=unhealthy" -q | wc -l)
if [ "$UNHEALTHY_CONTAINERS" -gt 0 ]; then
    echo "⚠️  WARNING: Some containers are unhealthy"
    $DOCKER_CMD ps --filter "health=unhealthy"
else
    echo "✅ All containers are healthy"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Available services:"
echo "   - App: https://novel-cloudtech.com:7443/"
echo "   - Grafana: https://novel-cloudtech.com:7443/grafana/ (or http://<ip>:3000)"
echo "   - Prometheus: http://<ip>:9093"
echo ""
echo "📝 Useful commands:"
echo "   - View logs: $DOCKER_CMD logs -f [service_name]"
echo "   - Restart service: $DOCKER_CMD restart [service_name]"
echo "   - Stop all: $DOCKER_CMD down"
echo ""
