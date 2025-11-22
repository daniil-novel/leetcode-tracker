from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class TaskBase(BaseModel):
    date: date
    platform: str = "leetcode"
    problem_id: Optional[str] = None
    title: Optional[str] = None
    difficulty: str  # "Easy" | "Medium" | "Hard"
    points: int
    notes: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int

    class Config:
        from_attributes = True


class DailyStat(BaseModel):
    date: date
    tasks_count: int
    xp_sum: int
    streak: int
    xp_cumulative: int


class MonthGoalBase(BaseModel):
    year: int
    month: int
    target_xp: int = 100


class MonthGoalCreate(MonthGoalBase):
    pass


class MonthGoal(MonthGoalBase):
    id: int

    class Config:
        from_attributes = True


class CalendarDay(BaseModel):
    date: date
    tasks_count: int
    xp_sum: int
    easy_count: int
    medium_count: int
    hard_count: int
    tasks: List[Task] = []


class MonthStats(BaseModel):
    year: int
    month: int
    target_xp: int
    current_xp: int
    total_tasks: int
    easy_count: int
    medium_count: int
    hard_count: int
    progress_percent: float
    calendar_days: List[CalendarDay]
