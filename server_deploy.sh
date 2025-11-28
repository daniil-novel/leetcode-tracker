#!/bin/bash

# Production Server Deployment Script
# Run this script ON THE PRODUCTION SERVER (novel-cloudtech.com)

set -e  # Exit on any error

echo "🚀 Production Server Deployment Script"
echo "========================================"
echo ""

# Step 1: Verify we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in project root directory!"
    echo "Please navigate to the leetcode_tracker_uv directory first"
    exit 1
fi

PROJECT_DIR=$(pwd)
echo "✅ Project directory: $PROJECT_DIR"
echo ""

# Step 2: Pull latest changes from git
echo "📥 Step 1: Pulling latest changes from git..."
git fetch origin
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Git pull failed!"
    exit 1
fi

echo "✅ Git pull successful"
echo ""

# Step 3: Verify frontend dist files exist
echo "📊 Step 2: Verifying frontend build files..."
if [ ! -d "frontend/dist" ]; then
    echo "❌ frontend/dist directory not found!"
    echo "Building frontend on server..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

if [ ! -f "frontend/dist/index.html" ]; then
    echo "❌ index.html not found!"
    exit 1
fi

echo "✅ Frontend files verified:"
ls -lh frontend/dist/
echo ""
ls -lh frontend/dist/assets/
echo ""

# Step 4: Check if CSS file contains Profile styles
echo "🔍 Step 3: Checking if Profile styles are in CSS..."
CSS_FILE=$(ls frontend/dist/assets/*.css 2>/dev/null | head -n 1)

if [ -z "$CSS_FILE" ]; then
    echo "❌ No CSS file found in dist/assets/"
    exit 1
fi

echo "CSS file: $CSS_FILE"

if grep -q "profile-page" "$CSS_FILE"; then
    echo "✅ Profile styles found in CSS file!"
else
    echo "❌ Profile styles NOT found in CSS file!"
    echo "Rebuilding frontend..."
    cd frontend
    rm -rf dist/
    npm run build
    cd ..
fi

echo ""

# Step 5: Restart the FastAPI service
echo "🔄 Step 4: Restarting leetcode-tracker service..."
sudo systemctl restart leetcode-tracker

if [ $? -ne 0 ]; then
    echo "❌ Service restart failed!"
    exit 1
fi

echo "✅ Service restarted"
echo ""

# Step 6: Wait for service to start
echo "⏳ Waiting for service to start..."
sleep 3

# Step 7: Check service status
echo "📊 Step 5: Checking service status..."
sudo systemctl status leetcode-tracker --no-pager -l

echo ""

# Step 8: Check recent logs
echo "📋 Step 6: Recent service logs..."
sudo journalctl -u leetcode-tracker -n 20 --no-pager

echo ""

# Step 9: Test if files are accessible
echo "🧪 Step 7: Testing file accessibility..."
echo ""

# Test index.html
echo "Testing index.html..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/

# Test CSS file
CSS_FILENAME=$(basename "$CSS_FILE")
echo "Testing CSS file: /assets/$CSS_FILENAME"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "http://localhost:8000/assets/$CSS_FILENAME"

echo ""

# Step 10: Final verification
echo "✅ Deployment completed!"
echo ""
echo "📋 Final steps:"
echo "1. Open browser and go to: https://novel-cloudtech.com/profile"
echo "2. Clear browser cache: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)"
echo "3. Or open in Incognito/Private mode"
echo "4. Verify that Profile styles are applied correctly"
echo ""
echo "🔍 To check if CSS is being served correctly:"
echo "curl -I https://novel-cloudtech.com/assets/$CSS_FILENAME"
echo ""
echo "📊 To monitor logs in real-time:"
echo "sudo journalctl -u leetcode-tracker -f"
echo ""
