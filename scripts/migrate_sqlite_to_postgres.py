#!/usr/bin/env python3
"""
Script to migrate data from SQLite to PostgreSQL.

This script:
1. Exports data from SQLite database
2. Imports data into PostgreSQL database

Usage:
    python scripts/migrate_sqlite_to_postgres.py
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import from leetcode_tracker
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from leetcode_tracker.models import Base, MonthGoal, SolvedTask, User


def export_from_sqlite(sqlite_url: str) -> dict:
    """Export all data from SQLite database."""
    print(f"Connecting to SQLite: {sqlite_url}")
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Export users
        users = session.query(User).all()
        users_data = [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "oauth_provider": u.oauth_provider,
                "oauth_id": u.oauth_id,
                "avatar_url": u.avatar_url,
                "leetcode_username": u.leetcode_username,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ]
        print(f"Exported {len(users_data)} users")

        # Export solved tasks
        tasks = session.query(SolvedTask).all()
        tasks_data = [
            {
                "id": t.id,
                "user_id": t.user_id,
                "date": t.date.isoformat() if t.date else None,
                "platform": t.platform,
                "problem_id": t.problem_id,
                "title": t.title,
                "difficulty": t.difficulty,
                "points": t.points,
                "time_spent": t.time_spent,
                "notes": t.notes,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tasks
        ]
        print(f"Exported {len(tasks_data)} solved tasks")

        # Export month goals
        goals = session.query(MonthGoal).all()
        goals_data = [
            {
                "id": g.id,
                "user_id": g.user_id,
                "year": g.year,
                "month": g.month,
                "target_xp": g.target_xp,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g in goals
        ]
        print(f"Exported {len(goals_data)} month goals")

        return {
            "users": users_data,
            "solved_tasks": tasks_data,
            "month_goals": goals_data,
        }
    finally:
        session.close()


def import_to_postgres(postgres_url: str, data: dict) -> None:
    """Import data into PostgreSQL database."""
    print(f"\nConnecting to PostgreSQL: {postgres_url}")
    engine = create_engine(postgres_url, pool_pre_ping=True)
    
    # Create all tables
    print("Creating tables...")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Import users
        print(f"\nImporting {len(data['users'])} users...")
        for user_data in data["users"]:
            user = User(
                id=user_data["id"],
                email=user_data["email"],
                username=user_data["username"],
                oauth_provider=user_data["oauth_provider"],
                oauth_id=user_data["oauth_id"],
                avatar_url=user_data["avatar_url"],
                leetcode_username=user_data["leetcode_username"],
            )
            session.add(user)
        session.commit()
        print("Users imported successfully")

        # Import solved tasks
        print(f"\nImporting {len(data['solved_tasks'])} solved tasks...")
        for task_data in data["solved_tasks"]:
            task = SolvedTask(
                id=task_data["id"],
                user_id=task_data["user_id"],
                date=task_data["date"],
                platform=task_data["platform"],
                problem_id=task_data["problem_id"],
                title=task_data["title"],
                difficulty=task_data["difficulty"],
                points=task_data["points"],
                time_spent=task_data["time_spent"],
                notes=task_data["notes"],
            )
            session.add(task)
        session.commit()
        print("Solved tasks imported successfully")

        # Import month goals
        print(f"\nImporting {len(data['month_goals'])} month goals...")
        for goal_data in data["month_goals"]:
            goal = MonthGoal(
                id=goal_data["id"],
                user_id=goal_data["user_id"],
                year=goal_data["year"],
                month=goal_data["month"],
                target_xp=goal_data["target_xp"],
            )
            session.add(goal)
        session.commit()
        print("Month goals imported successfully")

        # Update sequences for PostgreSQL
        print("\nUpdating sequences...")
        session.execute("SELECT setval('users_id_seq', (SELECT MAX(id) FROM users))")
        session.execute("SELECT setval('solved_tasks_id_seq', (SELECT MAX(id) FROM solved_tasks))")
        session.execute("SELECT setval('month_goals_id_seq', (SELECT MAX(id) FROM month_goals))")
        session.commit()
        print("Sequences updated successfully")

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def main():
    """Main migration function."""
    # Get database URLs from environment or use defaults
    sqlite_url = os.getenv("SQLITE_URL", "sqlite:///./leetcode.db")
    postgres_url = os.getenv("DATABASE_URL", "postgresql://leetcode_user:leetcode_password@localhost:5432/leetcode_tracker")

    print("=" * 60)
    print("SQLite to PostgreSQL Migration Script")
    print("=" * 60)
    print(f"\nSource (SQLite): {sqlite_url}")
    print(f"Target (PostgreSQL): {postgres_url}")
    print("\nThis will:")
    print("1. Export all data from SQLite")
    print("2. Create tables in PostgreSQL")
    print("3. Import all data to PostgreSQL")
    print("\nWARNING: This will overwrite existing data in PostgreSQL!")
    
    response = input("\nDo you want to continue? (yes/no): ")
    if response.lower() not in ["yes", "y"]:
        print("Migration cancelled.")
        return

    try:
        # Export from SQLite
        print("\n" + "=" * 60)
        print("Step 1: Exporting from SQLite")
        print("=" * 60)
        data = export_from_sqlite(sqlite_url)

        # Save backup
        backup_file = "migration_backup.json"
        print(f"\nSaving backup to {backup_file}...")
        with open(backup_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Backup saved successfully")

        # Import to PostgreSQL
        print("\n" + "=" * 60)
        print("Step 2: Importing to PostgreSQL")
        print("=" * 60)
        import_to_postgres(postgres_url, data)

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Users migrated: {len(data['users'])}")
        print(f"  - Solved tasks migrated: {len(data['solved_tasks'])}")
        print(f"  - Month goals migrated: {len(data['month_goals'])}")
        print(f"\nBackup saved to: {backup_file}")

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
