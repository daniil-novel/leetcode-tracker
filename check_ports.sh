#!/bin/bash
# Script to check what's using the ports

echo "Checking port 9091 (Prometheus)..."
sudo lsof -i :9091 || sudo netstat -tulpn | grep :9091

echo ""
echo "Checking port 8081 (cAdvisor)..."
sudo lsof -i :8081 || sudo netstat -tulpn | grep :8081

echo ""
echo "Checking all Docker containers..."
docker ps -a

echo ""
echo "Checking Docker networks..."
docker network ls
