#!/usr/bin/env python3
"""
Script to create test data in PostgreSQL database for testing Grafana dashboards.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from leetcode_tracker.models import Base, MonthGoal, SolvedTask, User


def create_test_data():
    """Create test data in the database."""
    # Connect to PostgreSQL
    postgres_url = "postgresql://leetcode_user:leetcode_password@localhost:5432/leetcode_tracker"
    print(f"Connecting to PostgreSQL: {postgres_url}")
    
    engine = create_engine(postgres_url, pool_pre_ping=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create test user
        print("\nCreating test user...")
        user = User(
            username="test_user",
            email="test@example.com",
            oauth_provider="github",
            oauth_id="123456",
            leetcode_username="test_leetcode_user"
        )
        session.add(user)
        session.commit()
        print(f"Created user: {user.username} (ID: {user.id})")

        # Create test tasks for the last 30 days
        print("\nCreating test tasks...")
        today = date.today()
        difficulties = ["Easy", "Medium", "Hard"]
        points_map = {"Easy": 1, "Medium": 3, "Hard": 5}
        
        task_count = 0
        for i in range(30):
            task_date = today - timedelta(days=i)
            # Create 1-3 tasks per day
            num_tasks = (i % 3) + 1
            
            for j in range(num_tasks):
                difficulty = difficulties[j % 3]
                task = SolvedTask(
                    user_id=user.id,
                    date=task_date,
                    platform="leetcode",
                    problem_id=f"{1000 + task_count}",
                    title=f"Test Problem {task_count + 1}",
                    difficulty=difficulty,
                    points=points_map[difficulty],
                    time_spent=15 + (j * 10),  # 15, 25, 35 minutes
                    notes=f"Test task {task_count + 1}"
                )
                session.add(task)
                task_count += 1
        
        session.commit()
        print(f"Created {task_count} test tasks")

        # Create month goal
        print("\nCreating month goal...")
        goal = MonthGoal(
            user_id=user.id,
            year=today.year,
            month=today.month,
            target_xp=100
        )
        session.add(goal)
        session.commit()
        print(f"Created month goal: {goal.target_xp} XP for {goal.year}-{goal.month}")

        # Print summary
        print("\n" + "=" * 60)
        print("Test data created successfully!")
        print("=" * 60)
        print(f"User: {user.username}")
        print(f"Tasks: {task_count}")
        print(f"Date range: {today - timedelta(days=29)} to {today}")
        
        # Calculate stats
        total_xp = session.query(SolvedTask).filter(SolvedTask.user_id == user.id).count()
        easy_count = session.query(SolvedTask).filter(
            SolvedTask.user_id == user.id,
            SolvedTask.difficulty == "Easy"
        ).count()
        medium_count = session.query(SolvedTask).filter(
            SolvedTask.user_id == user.id,
            SolvedTask.difficulty == "Medium"
        ).count()
        hard_count = session.query(SolvedTask).filter(
            SolvedTask.user_id == user.id,
            SolvedTask.difficulty == "Hard"
        ).count()
        
        print(f"\nDifficulty breakdown:")
        print(f"  Easy: {easy_count}")
        print(f"  Medium: {medium_count}")
        print(f"  Hard: {hard_count}")
        print(f"\nTotal tasks: {total_xp}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    create_test_data()
