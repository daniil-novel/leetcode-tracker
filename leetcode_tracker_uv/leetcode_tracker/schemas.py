from datetime import date
from typing import Optional

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
        orm_mode = True


class DailyStat(BaseModel):
    date: date
    tasks_count: int
    xp_sum: int
    streak: int
    xp_cumulative: int
