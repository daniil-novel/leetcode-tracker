#!/bin/bash
# Emergency cleanup script for Docker containers and ports

echo "🧹 Emergency Docker cleanup..."

# Stop all project containers
echo "Stopping all project containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Force remove containers by name
echo "Force removing containers by name..."
docker ps -a --filter "name=leetcode" -q | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=prometheus" -q | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=grafana" -q | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=cadvisor" -q | xargs -r docker rm -f 2>/dev/null || true
docker ps -a --filter "name=node_exporter" -q | xargs -r docker rm -f 2>/dev/null || true

# Remove dangling containers
echo "Removing dangling containers..."
docker container prune -f 2>/dev/null || true

# Show what's still running
echo ""
echo "Remaining containers:"
docker ps -a

echo ""
echo "Port usage check:"
echo "Port 9091 (occupied by external process):"
sudo netstat -tulpn | grep :9091 || echo "  ✅ Port 9091 is free"
echo "Port 9092 (Prometheus - new):"
sudo netstat -tulpn | grep :9092 || echo "  ✅ Port 9092 is free"
echo "Port 8081 (cAdvisor):"
sudo netstat -tulpn | grep :8081 || echo "  ✅ Port 8081 is free"
echo "Port 3000 (Grafana):"
sudo netstat -tulpn | grep :3000 || echo "  ✅ Port 3000 is free"
echo "Port 8000 (App):"
sudo netstat -tulpn | grep :8000 || echo "  ✅ Port 8000 is free"

echo ""
echo "✅ Cleanup complete! You can now run ./deploy.sh"
