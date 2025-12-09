#!/usr/bin/env python3
"""Fix dashboard UIDs to match datasource UID."""

import json

# Read the dashboard file
with open('grafana/provisioning/dashboards/leetcode-tracker.json', 'r', encoding='utf-8') as f:
    dashboard = json.load(f)

# Replace all UIDs
def replace_uids(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key == 'uid' and value == 'LeetCode Tracker PostgreSQL':
                obj[key] = 'leetcode-tracker-postgres'
            else:
                replace_uids(value)
    elif isinstance(obj, list):
        for item in obj:
            replace_uids(item)

replace_uids(dashboard)

# Write back
with open('grafana/provisioning/dashboards/leetcode-tracker.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard, f, indent=2)

print("✅ Fixed all datasource UIDs in dashboard!")
