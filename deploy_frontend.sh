#!/bin/bash

# Frontend Deployment Script for novel-cloudtech.com
# This script builds the frontend and restarts the FastAPI service

echo "🚀 Starting frontend deployment..."

# Navigate to frontend directory
cd frontend || exit 1

echo "📦 Building frontend..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build completed successfully!"

# Check if we're on the production server
if [ -f "/etc/systemd/system/leetcode-tracker.service" ]; then
    echo "🔄 Restarting FastAPI service..."
    sudo systemctl restart leetcode-tracker
    
    echo "📊 Checking service status..."
    sudo systemctl status leetcode-tracker --no-pager
    
    echo "✅ Deployment completed!"
else
    echo "⚠️  Not on production server. Please manually restart FastAPI."
    echo "   On production, run: sudo systemctl restart leetcode-tracker"
fi

echo ""
echo "📝 Next steps:"
echo "   1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)"
echo "   2. Visit https://novel-cloudtech.com/profile"
echo "   3. Verify styles are applied correctly"
