#!/bin/bash

# Script to update leetcode-tracker systemd service on the server
# This script should be run on the server after pulling the latest code

set -e  # Exit on error

echo "🔄 Updating LeetCode Tracker systemd service..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Error: This script must be run as root"
    exit 1
fi

# Check if service file exists in current directory
if [ ! -f "leetcode-tracker.service" ]; then
    echo "❌ Error: leetcode-tracker.service file not found in current directory"
    exit 1
fi

# Backup current service file if it exists
if [ -f "/etc/systemd/system/leetcode-tracker.service" ]; then
    echo "📦 Backing up current service file..."
    cp /etc/systemd/system/leetcode-tracker.service /etc/systemd/system/leetcode-tracker.service.backup
fi

# Stop the service
echo "⏸️  Stopping leetcode-tracker service..."
systemctl stop leetcode-tracker

# Copy new service file
echo "📝 Copying new service file..."
cp leetcode-tracker.service /etc/systemd/system/

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable service (in case it wasn't enabled)
echo "✅ Enabling service..."
systemctl enable leetcode-tracker

# Start the service
echo "▶️  Starting leetcode-tracker service..."
systemctl start leetcode-tracker

# Wait a moment for service to start
sleep 2

# Check status
echo ""
echo "📊 Service status:"
systemctl status leetcode-tracker --no-pager

echo ""
echo "✅ Service update complete!"
echo ""
echo "📋 Useful commands:"
echo "  View logs: journalctl -u leetcode-tracker -f"
echo "  Restart: systemctl restart leetcode-tracker"
echo "  Status: systemctl status leetcode-tracker"
