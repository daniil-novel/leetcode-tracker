#!/bin/bash
# Script to apply database migration on the server

echo "🔄 Applying database migration..."

# Navigate to project directory
cd /home/daniil/leetcode-tracker

# Apply migration
uv run alembic upgrade head

echo "✅ Migration applied successfully!"
