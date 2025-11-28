import json
import sys
from datetime import date, datetime
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from leetcode_tracker.database import SessionLocal
from leetcode_tracker.models import MonthGoal, SolvedTask, User


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def export_data():
    db: Session = SessionLocal()
    try:
        data = {
            "users": [],
            "solved_tasks": [],
            "month_goals": []
        }

        # Export Users
        users = db.query(User).all()
        for user in users:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "oauth_provider": user.oauth_provider,
                "oauth_id": user.oauth_id,
                "avatar_url": user.avatar_url,
                "leetcode_username": user.leetcode_username,
                "created_at": user.created_at
            }
            data["users"].append(user_dict)

        # Export SolvedTasks
        tasks = db.query(SolvedTask).all()
        for task in tasks:
            task_dict = {
                "id": task.id,
                "user_id": task.user_id,
                "date": task.date,
                "platform": task.platform,
                "problem_id": task.problem_id,
                "title": task.title,
                "difficulty": task.difficulty,
                "points": task.points,
                "time_spent": task.time_spent,
                "notes": task.notes,
                "created_at": task.created_at
            }
            data["solved_tasks"].append(task_dict)

        # Export MonthGoals
        goals = db.query(MonthGoal).all()
        for goal in goals:
            goal_dict = {
                "id": goal.id,
                "user_id": goal.user_id,
                "year": goal.year,
                "month": goal.month,
                "target_xp": goal.target_xp,
                "created_at": goal.created_at
            }
            data["month_goals"].append(goal_dict)

        output_file = "leetcode_tracker_export.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, default=json_serial, indent=2, ensure_ascii=False)
        
        print(f"✅ Data exported successfully to {output_file}")
        print(f"   - Users: {len(data['users'])}")
        print(f"   - Tasks: {len(data['solved_tasks'])}")
        print(f"   - Goals: {len(data['month_goals'])}")

    except Exception as e:
        print(f"❌ Export failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    export_data()
