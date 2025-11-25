from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from .database import Base


class SolvedTask(Base):
    __tablename__ = "solved_tasks"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    platform = Column(String(50), nullable=False, default="leetcode")
    problem_id = Column(String(50), nullable=True)
    title = Column(String(200), nullable=True)
    difficulty = Column(String(10), nullable=False)  # Easy / Medium / Hard
    points = Column(Integer, nullable=False)  # XP
    time_spent = Column(Integer, nullable=True)  # Time in minutes
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MonthGoal(Base):
    __tablename__ = "month_goals"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    target_xp = Column(Integer, nullable=False, default=100)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
