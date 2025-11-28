#!/bin/bash

echo "=========================================="
echo "LeetCode Tracker 502 Error Fix Script"
echo "=========================================="
echo ""

# Navigate to project directory
cd /root/leetcode_tracker_uv

echo "Step 1: Stopping the service..."
systemctl stop leetcode-tracker
sleep 2

echo "Step 2: Syncing dependencies with uv..."
/root/.local/bin/uv sync
echo ""

echo "Step 3: Checking .env file..."
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file with required variables:"
    echo "  - SECRET_KEY"
    echo "  - GITHUB_CLIENT_ID"
    echo "  - GITHUB_CLIENT_SECRET"
    exit 1
fi
echo "✓ .env file exists"
echo ""

echo "Step 4: Checking frontend build..."
if [ ! -d frontend/dist ]; then
    echo "WARNING: Frontend dist not found. Building frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
fi
echo "✓ Frontend build exists"
echo ""

echo "Step 5: Testing application startup..."
timeout 10 /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 127.0.0.1 --port 8001 &
TEST_PID=$!
sleep 5

# Check if the test process is still running
if ps -p $TEST_PID > /dev/null; then
    echo "✓ Application starts successfully"
    kill $TEST_PID 2>/dev/null
else
    echo "✗ Application failed to start. Check the error above."
    exit 1
fi
echo ""

echo "Step 6: Reloading systemd daemon..."
systemctl daemon-reload
echo ""

echo "Step 7: Starting the service..."
systemctl start leetcode-tracker
sleep 3
echo ""

echo "Step 8: Checking service status..."
systemctl status leetcode-tracker --no-pager
echo ""

echo "Step 9: Checking if port 8000 is listening..."
sleep 2
netstat -tlnp | grep 8000 || ss -tlnp | grep 8000
echo ""

echo "Step 10: Testing nginx connection..."
curl -I http://127.0.0.1:8000/ 2>&1 | head -5
echo ""

echo "=========================================="
echo "Fix script complete!"
echo ""
echo "If the service is running, try accessing:"
echo "https://novel-cloudtech.com:7443"
echo ""
echo "If still getting 502, check logs with:"
echo "journalctl -u leetcode-tracker -n 50 --no-pager"
echo "=========================================="
