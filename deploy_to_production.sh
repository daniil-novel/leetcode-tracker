#!/bin/bash

# Complete deployment script for novel-cloudtech.com
# This script ensures all changes are properly deployed

set -e  # Exit on any error

echo "🚀 Starting complete deployment process..."
echo ""

# Step 1: Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in project root directory!"
    echo "Please run this script from the leetcode_tracker_uv directory"
    exit 1
fi

echo "✅ In correct directory"
echo ""

# Step 2: Build frontend locally
echo "📦 Step 1: Building frontend..."
cd frontend

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf dist/

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing npm dependencies..."
    npm install
fi

# Build
echo "🔨 Building..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build completed successfully!"
echo ""

# Step 3: Verify build output
echo "📊 Step 2: Verifying build output..."
if [ ! -d "dist" ]; then
    echo "❌ dist directory not found!"
    exit 1
fi

if [ ! -f "dist/index.html" ]; then
    echo "❌ index.html not found in dist!"
    exit 1
fi

echo "✅ Build files verified:"
ls -lh dist/
echo ""
ls -lh dist/assets/
echo ""

cd ..

# Step 4: Git operations
echo "📝 Step 3: Committing changes to git..."
git add frontend/dist/
git add frontend/src/
git status

read -p "Do you want to commit these changes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Deploy: Update frontend build with Profile.css styles"
    
    read -p "Do you want to push to remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin main
        echo "✅ Changes pushed to remote"
    fi
else
    echo "⚠️  Skipping commit"
fi

echo ""
echo "📋 Next steps for production server:"
echo ""
echo "Run these commands on novel-cloudtech.com:"
echo ""
echo "# 1. Connect to server"
echo "ssh user@novel-cloudtech.com"
echo ""
echo "# 2. Navigate to project directory"
echo "cd /path/to/leetcode_tracker_uv"
echo ""
echo "# 3. Pull latest changes"
echo "git pull origin main"
echo ""
echo "# 4. Verify files are updated"
echo "ls -lh frontend/dist/assets/"
echo ""
echo "# 5. Restart the service"
echo "sudo systemctl restart leetcode-tracker"
echo ""
echo "# 6. Check service status"
echo "sudo systemctl status leetcode-tracker"
echo ""
echo "# 7. Check logs"
echo "sudo journalctl -u leetcode-tracker -n 50 --no-pager"
echo ""
echo "# 8. Test in browser (clear cache with Ctrl+Shift+R)"
echo "curl -I https://novel-cloudtech.com/assets/index-eGHtU6UY.css"
echo ""
