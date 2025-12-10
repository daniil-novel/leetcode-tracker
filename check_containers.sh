#!/bin/bash
# Check all containers and find the app container

echo "=== All containers (including stopped) ==="
docker ps -a

echo ""
echo "=== Looking for app container by different names ==="
docker ps -a | grep -E "app|leetcode"

echo ""
echo "=== Docker compose services status ==="
docker-compose ps

echo ""
echo "=== Checking if app container exists with ID ==="
docker ps -a --filter "id=d5dfcc980c78"

echo ""
echo "=== Logs of container d5dfcc980c78 (if exists) ==="
docker logs d5dfcc980c78 2>&1 || echo "Container d5dfcc980c78 not found or removed"

echo ""
echo "=== Checking docker-compose logs for app service ==="
docker-compose logs app 2>&1 | tail -50 || echo "No logs for app service"
