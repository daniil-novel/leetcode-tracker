#!/bin/bash

# Updated at 2025-12-10 02:42
# Stop on error
set -e

echo "🚀 Starting deployment (v2)..."

# 1. Stop systemd service if it exists and is running
if systemctl is-active --quiet leetcode-tracker.service; then
    echo "🛑 Stopping legacy systemd service..."
    sudo systemctl stop leetcode-tracker.service
    sudo systemctl disable leetcode-tracker.service
    echo "✅ Systemd service stopped and disabled."
fi

# 2. Pull latest changes
echo "📥 Pulling latest code..."
git pull

# 3. Determine Docker command
echo "🔍 Checking Docker environment..."
if command -v docker-compose >/dev/null 2>&1; then
    echo "✅ Found 'docker-compose' (standalone)"
    DOCKER_CMD="docker-compose"
else
    echo "⚠️ 'docker-compose' not found, trying 'docker compose' (plugin)"
    DOCKER_CMD="docker compose"
fi

# 4. Stop and remove old containers to avoid ContainerConfig errors
echo "🧹 Cleaning up old containers..."
$DOCKER_CMD down --remove-orphans || true

# 5. Build and start containers
echo "🐳 Building and starting containers using: $DOCKER_CMD"
$DOCKER_CMD up -d --build

# 6. Run migrations
echo "🔄 Running database migrations..."
sleep 5
$DOCKER_CMD exec -T app uv run alembic upgrade head

echo "✅ Deployment complete!"
echo "📊 Grafana: https://novel-cloudtech.com:7443/grafana/ (or http://<ip>:3000)"
echo "🌐 App: https://novel-cloudtech.com:7443/"
