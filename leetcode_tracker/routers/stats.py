from datetime import date, timedelta
from typing import List
from collections import defaultdict
import calendar

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from ..dependencies import get_db, get_current_user
from .. import models, schemas

router = APIRouter()


@router.get("/api/stats/time")
def get_time_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time statistics for tasks with time_spent data."""
    tasks = (
        db.query(models.SolvedTask)
        .filter(
            models.SolvedTask.user_id == current_user.id,
            models.SolvedTask.time_spent.isnot(None)
        )
        .order_by(models.SolvedTask.date.asc())
        .all()
    )
    
    if not tasks:
        return {
            "tasks": [],
            "average_time": 0,
            "total_time": 0,
            "avg_by_difficulty": {
                "Easy": 0,
                "Medium": 0,
                "Hard": 0
            }
        }
    
    # Calculate average time by difficulty
    time_by_difficulty = {"Easy": [], "Medium": [], "Hard": []}
    for task in tasks:
        if task.time_spent and task.difficulty in time_by_difficulty:
            time_by_difficulty[task.difficulty].append(task.time_spent)
    
    avg_by_difficulty = {
        diff: (sum(times) / len(times) if times else 0)
        for diff, times in time_by_difficulty.items()
    }
    
    total_time = sum(t.time_spent for t in tasks if t.time_spent)
    average_time = total_time / len(tasks) if tasks else 0
    
    # Format tasks for chart
    task_list = [
        {
            "id": t.id,
            "title": t.title or (f"Task #{t.problem_id}" if t.problem_id else f"Task {t.id}"),
            "difficulty": t.difficulty,
            "time_spent": t.time_spent,
            "date": str(t.date),
            "points": t.points
        }
        for t in tasks
    ]
    
    return {
        "tasks": task_list,
        "average_time": round(average_time, 1),
        "total_time": total_time,
        "avg_by_difficulty": {k: round(v, 1) for k, v in avg_by_difficulty.items()}
    }


@router.get("/api/stats/daily", response_model=list[schemas.DailyStat])
def api_daily_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aggregate stats per day for current user."""
    rows = (
        db.query(models.SolvedTask.date)
        .filter(models.SolvedTask.user_id == current_user.id)
        .distinct()
        .order_by(models.SolvedTask.date.asc())
        .all()
    )

    if not rows:
        return []

    all_dates: list[date] = []
    if rows:
      cur = rows[0][0]
      last = rows[-1][0]
      while cur <= last:
          all_dates.append(cur)
          cur = cur + timedelta(days=1)


    count_by_date: dict[date, int] = defaultdict(int)
    xp_by_date: dict[date, int] = defaultdict(int)

    tasks = db.query(models.SolvedTask).filter(
        models.SolvedTask.user_id == current_user.id
    ).all()
    
    for t in tasks:
        count_by_date[t.date] += 1
        xp_by_date[t.date] += t.points

    stats: list[schemas.DailyStat] = []
    streak = 0
    xp_cum = 0
    for d in all_dates:
        tasks_count = count_by_date[d]
        xp_sum = xp_by_date[d]
        if tasks_count > 0:
            streak += 1
        else:
            streak = 0
        xp_cum += xp_sum
        stats.append(
            schemas.DailyStat(
                date=d,
                tasks_count=tasks_count,
                xp_sum=xp_sum,
                streak=streak,
                xp_cumulative=xp_cum,
            )
        )

    return stats


@router.get("/api/month/goal/{year}/{month}", response_model=schemas.MonthGoal)
def get_month_goal(
    year: int,
    month: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get or create month goal for current user."""
    goal = (
        db.query(models.MonthGoal)
        .filter(
            models.MonthGoal.user_id == current_user.id,
            models.MonthGoal.year == year,
            models.MonthGoal.month == month
        )
        .first()
    )
    
    if not goal:
        goal = models.MonthGoal(
            user_id=current_user.id,
            year=year,
            month=month,
            target_xp=100
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
    
    return goal


@router.post("/api/month/goal")
def set_month_goal(
    goal_data: schemas.MonthGoalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set month goal for current user."""
    existing = (
        db.query(models.MonthGoal)
        .filter(
            models.MonthGoal.user_id == current_user.id,
            models.MonthGoal.year == goal_data.year,
            models.MonthGoal.month == goal_data.month
        )
        .first()
    )
    
    if existing:
        existing.target_xp = goal_data.target_xp
        db.commit()
        db.refresh(existing)
        return existing
    else:
        goal = models.MonthGoal(
            **goal_data.dict(),
            user_id=current_user.id
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal


@router.get("/api/month/stats/{year}/{month}", response_model=schemas.MonthStats)
def get_month_stats(
    year: int,
    month: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete month statistics for current user."""
    # Get or create goal
    goal = (
        db.query(models.MonthGoal)
        .filter(
            models.MonthGoal.user_id == current_user.id,
            models.MonthGoal.year == year,
            models.MonthGoal.month == month
        )
        .first()
    )
    
    if not goal:
        goal = models.MonthGoal(
            user_id=current_user.id,
            year=year,
            month=month,
            target_xp=100
        )
        db.add(goal)
        db.commit()
    
    # Get all tasks for this month
    tasks = (
        db.query(models.SolvedTask)
        .filter(
            models.SolvedTask.user_id == current_user.id,
            extract('year', models.SolvedTask.date) == year,
            extract('month', models.SolvedTask.date) == month
        )
        .order_by(models.SolvedTask.date.asc())
        .all()
    )
    
    # Calculate stats
    total_xp = sum(t.points for t in tasks)
    total_tasks = len(tasks)
    easy_count = len([t for t in tasks if t.difficulty == 'Easy'])
    medium_count = len([t for t in tasks if t.difficulty == 'Medium'])
    hard_count = len([t for t in tasks if t.difficulty == 'Hard'])
    progress = (total_xp / goal.target_xp * 100) if goal.target_xp > 0 else 0
    
    # Build calendar
    _, num_days = calendar.monthrange(year, month)
    calendar_days = []
    
    # Group tasks by date
    tasks_by_date = defaultdict(list)
    for task in tasks:
        tasks_by_date[task.date].append(task)
    
    # Create calendar days
    for day in range(1, num_days + 1):
        day_date = date(year, month, day)
        day_tasks = tasks_by_date.get(day_date, [])
        
        day_xp = sum(t.points for t in day_tasks)
        day_easy = len([t for t in day_tasks if t.difficulty == 'Easy'])
        day_medium = len([t for t in day_tasks if t.difficulty == 'Medium'])
        day_hard = len([t for t in day_tasks if t.difficulty == 'Hard'])
        
        calendar_days.append(schemas.CalendarDay(
            date=day_date,
            tasks_count=len(day_tasks),
            xp_sum=day_xp,
            easy_count=day_easy,
            medium_count=day_medium,
            hard_count=day_hard,
            tasks=day_tasks
        ))
    
    return schemas.MonthStats(
        year=year,
        month=month,
        target_xp=goal.target_xp,
        current_xp=total_xp,
        total_tasks=total_tasks,
        easy_count=easy_count,
        medium_count=medium_count,
        hard_count=hard_count,
        progress_percent=progress,
        calendar_days=calendar_days
    )
