"""Script to reset the database - deletes old DB and creates new one with current schema."""

import os
from pathlib import Path

# Find and delete old database
db_files = ["leetcode_tracker.db", "leetcode_tracker.sqlite", "leetcode_tracker.sqlite3"]
for db_file in db_files:
    if os.path.exists(db_file):
        print(f"Deleting old database: {db_file}")
        os.remove(db_file)
        print(f"✅ Deleted {db_file}")

# Also check in current directory and parent
for parent in [".", ".."]:
    for db_file in db_files:
        full_path = os.path.join(parent, db_file)
        if os.path.exists(full_path):
            print(f"Deleting old database: {full_path}")
            os.remove(full_path)
            print(f"✅ Deleted {full_path}")

print("\n✅ Database reset complete!")
print("Now run: uv run uvicorn leetcode_tracker.main:app --reload")
print("The new database will be created automatically with the correct schema.")
