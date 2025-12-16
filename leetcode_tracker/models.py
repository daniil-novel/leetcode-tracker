from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    oauth_provider = Column(String(20), nullable=True)  # 'github'
    oauth_id = Column(String(255), nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)
    leetcode_username = Column(String(100), nullable=True, index=True)  # LeetCode username for API sync

    # LeetCode Stats
    ranking = Column(Integer, nullable=True)
    reputation = Column(Integer, nullable=True)
    total_solved = Column(Integer, nullable=True)
    easy_solved = Column(Integer, nullable=True)
    medium_solved = Column(Integer, nullable=True)
    hard_solved = Column(Integer, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tasks = relationship("SolvedTask", back_populates="user", cascade="all, delete-orphan")
    month_goals = relationship("MonthGoal", back_populates="user", cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SolvedTask(Base):
    __tablename__ = "solved_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    date = Column(Date, nullable=False, index=True)
    platform = Column(String(50), nullable=False, default="leetcode")
    problem_id = Column(String(50), nullable=True)
    title = Column(String(200), nullable=True)
    difficulty = Column(String(10), nullable=False)  # Easy / Medium / Hard
    points = Column(Integer, nullable=False)  # XP
    time_spent = Column(Integer, nullable=True)  # Time in minutes
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MonthGoal(Base):
    __tablename__ = "month_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    target_xp = Column(Integer, nullable=False, default=100)

    # Relationships
    user = relationship("User", back_populates="month_goals")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
