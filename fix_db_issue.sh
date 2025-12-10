#!/bin/bash
# Script to diagnose and fix database issues

echo "=== Database container logs ==="
docker logs leetcode-tracker-db --tail 100

echo ""
echo "=== Checking database volume ==="
docker volume inspect leetcode_tracker_uv_postgres_data

echo ""
echo "=== Stopping all containers ==="
docker-compose down

echo ""
echo "=== Removing database container and volume (WARNING: This will delete all data!) ==="
read -p "Do you want to remove the database volume? This will DELETE ALL DATA! (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    docker volume rm leetcode_tracker_uv_postgres_data
    echo "Volume removed. Starting fresh deployment..."
    docker-compose up -d
else
    echo "Volume not removed. Trying to restart without removing volume..."
    docker-compose up -d
fi

echo ""
echo "=== Waiting for containers to start ==="
sleep 10

echo ""
echo "=== Checking container status ==="
docker-compose ps

echo ""
echo "=== Database logs after restart ==="
docker logs leetcode-tracker-db --tail 50
