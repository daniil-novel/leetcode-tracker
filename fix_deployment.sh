#!/bin/bash
# Script to diagnose and fix deployment issues

echo "=== STEP 1: Checking current Docker containers ==="
docker ps -a

echo ""
echo "=== STEP 2: Removing zombie prometheus container ==="
docker rm -f 489dae8029f7 2>/dev/null || docker rm -f $(docker ps -a --filter "name=prometheus" -q) 2>/dev/null || echo "No prometheus container found"

echo ""
echo "=== STEP 3: Checking which processes occupy ports ==="
echo "Port 9091:"
sudo netstat -tulpn | grep :9091
echo ""
echo "Port 9092:"
sudo netstat -tulpn | grep :9092
echo ""
echo "Port 9093:"
sudo netstat -tulpn | grep :9093 || echo "Port 9093 is FREE ✅"

echo ""
echo "=== STEP 4: Checking all occupied ports in range 9090-9100 ==="
sudo netstat -tulpn | grep -E ':(909[0-9]|910[0-9])'

echo ""
echo "=== RECOMMENDATIONS ==="
echo "1. Ports 9091 and 9092 are occupied by external processes (not Docker)"
echo "2. We need to change Prometheus port to 9093 or another free port"
echo "3. The zombie prometheus container will be removed"
echo ""
echo "Do you want to:"
echo "  A) Change Prometheus port to 9093 (recommended)"
echo "  B) Stop the processes on ports 9091/9092 (risky - may break other services)"
echo ""
echo "Please respond with your choice."
