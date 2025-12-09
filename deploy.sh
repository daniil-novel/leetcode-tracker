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
docker compose up -d --build

# 4. Run migrations
echo "🔄 Running database migrations..."
# Wait for DB to be ready
sleep 5
docker compose exec app uv run alembic upgrade head

echo "✅ Deployment complete!"
echo "📊 Grafana: https://novel-cloudtech.com:7443/grafana/ (or http://<ip>:3000)"
echo "🌐 App: https://novel-cloudtech.com:7443/"
