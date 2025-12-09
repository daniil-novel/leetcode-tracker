#!/bin/bash

# Stop on error
set -e

echo "🚀 Starting deployment..."

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

# 3. Build and start containers
echo "🐳 Building and starting Docker containers..."

# Check if docker-compose (dash) exists, otherwise try docker compose (space)
if command -v docker-compose &> /dev/null; then
    echo "Using docker-compose (dash)..."
    docker-compose up -d --build
    
    # Run migrations
    echo "🔄 Running database migrations..."
    sleep 5
    docker-compose exec -T app uv run alembic upgrade head
else
    echo "Using docker compose (space)..."
    docker compose up -d --build
    
    # Run migrations
    echo "🔄 Running database migrations..."
    sleep 5
    docker compose exec -T app uv run alembic upgrade head
fi

echo "✅ Deployment complete!"
echo "📊 Grafana: https://novel-cloudtech.com:7443/grafana/ (or http://<ip>:3000)"
echo "🌐 App: https://novel-cloudtech.com:7443/"
