#!/usr/bin/env python3
"""Fix dashboard datasource type to sqlite for server."""

import json

def replace_datasource_type(obj):
    if isinstance(obj, dict):
        if 'datasource' in obj:
            ds = obj['datasource']
            if isinstance(ds, dict) and ds.get('type') == 'postgres':
                ds['type'] = 'sqlite'
        for v in obj.values():
            replace_datasource_type(v)
    elif isinstance(obj, list):
        for item in obj:
            replace_datasource_type(item)

with open('grafana/provisioning/dashboards/leetcode-tracker.json', 'r', encoding='utf-8') as f:
    dashboard = json.load(f)

replace_datasource_type(dashboard)

with open('grafana/provisioning/dashboards/leetcode-tracker-server.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard, f, indent=2)

print("✅ Fixed datasource type to sqlite, saved as leetcode-tracker-server.json")
