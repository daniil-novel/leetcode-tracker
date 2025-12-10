#!/bin/bash
# Script to diagnose app container issues

echo "=== Checking app container status ==="
docker ps -a | grep leetcode-tracker-app

echo ""
echo "=== App container logs (last 50 lines) ==="
docker logs leetcode-tracker-app --tail 50

echo ""
echo "=== Checking database container ==="
docker ps -a | grep leetcode-tracker-db

echo ""
echo "=== Database logs (last 20 lines) ==="
docker logs leetcode-tracker-db --tail 20

echo ""
echo "=== Testing database connection from app container ==="
docker exec leetcode-tracker-app curl -f http://localhost:8000/health 2>&1 || echo "Health check failed"

echo ""
echo "=== Checking if app is listening on port 8000 ==="
docker exec leetcode-tracker-app netstat -tulpn 2>/dev/null || docker exec leetcode-tracker-app ss -tulpn 2>/dev/null || echo "Cannot check ports"

echo ""
echo "=== Testing database connection directly ==="
docker exec leetcode-tracker-db psql -U leetcode_user -d leetcode_tracker -c "SELECT 1;" 2>&1

echo ""
echo "=== Checking app container environment ==="
docker exec leetcode-tracker-app env | grep -E "DATABASE_URL|PYTHONPATH|PATH" | head -10

echo ""
echo "=== Inspecting app healthcheck ==="
docker inspect leetcode-tracker-app | grep -A 20 "Health"
