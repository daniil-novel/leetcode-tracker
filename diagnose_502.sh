#!/bin/bash

echo "=========================================="
echo "LeetCode Tracker 502 Error Diagnostic"
echo "=========================================="
echo ""

# Check if service is running
echo "1. Checking systemd service status..."
systemctl status leetcode-tracker --no-pager
echo ""

# Check service logs
echo "2. Checking recent service logs..."
journalctl -u leetcode-tracker -n 50 --no-pager
echo ""

# Check if port 8000 is listening
echo "3. Checking if port 8000 is listening..."
netstat -tlnp | grep 8000 || ss -tlnp | grep 8000
echo ""

# Check nginx status
echo "4. Checking nginx status..."
systemctl status nginx --no-pager
echo ""

# Check nginx error logs
echo "5. Checking nginx error logs..."
tail -n 30 /var/log/nginx/novel-cloudtech.com.error.log
echo ""

# Check if .env file exists
echo "6. Checking .env file..."
if [ -f /root/leetcode_tracker_uv/.env ]; then
    echo ".env file exists"
    echo "Required variables check:"
    grep -q "SECRET_KEY" /root/leetcode_tracker_uv/.env && echo "✓ SECRET_KEY found" || echo "✗ SECRET_KEY missing"
    grep -q "GITHUB_CLIENT_ID" /root/leetcode_tracker_uv/.env && echo "✓ GITHUB_CLIENT_ID found" || echo "✗ GITHUB_CLIENT_ID missing"
    grep -q "GITHUB_CLIENT_SECRET" /root/leetcode_tracker_uv/.env && echo "✓ GITHUB_CLIENT_SECRET found" || echo "✗ GITHUB_CLIENT_SECRET missing"
else
    echo "✗ .env file NOT found!"
fi
echo ""

# Check if frontend dist exists
echo "7. Checking frontend build..."
if [ -d /root/leetcode_tracker_uv/frontend/dist ]; then
    echo "✓ Frontend dist directory exists"
    ls -la /root/leetcode_tracker_uv/frontend/dist/ | head -10
else
    echo "✗ Frontend dist directory NOT found!"
fi
echo ""

# Try to start the app manually to see errors
echo "8. Testing manual app startup..."
cd /root/leetcode_tracker_uv
timeout 5 /root/.local/bin/uv run uvicorn leetcode_tracker.main:app --host 127.0.0.1 --port 8001 2>&1 || echo "Manual startup test completed"
echo ""

# Check Python dependencies
echo "9. Checking Python dependencies..."
cd /root/leetcode_tracker_uv
/root/.local/bin/uv pip list 2>&1 | grep -E "(fastapi|uvicorn|sqlalchemy|pydantic|authlib)" || echo "Dependencies check completed"
echo ""

echo "=========================================="
echo "Diagnostic complete!"
echo "=========================================="
