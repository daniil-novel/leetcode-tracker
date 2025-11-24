from sqlalchemy import Column, Integer, String, Date, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # For local authentication
    oauth_provider = Column(String(20), nullable=True)  # 'github' or 'google'
    oauth_id = Column(String(255), nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    tasks = relationship("SolvedTask", back_populates="user", cascade="all, delete-orphan")
    month_goals = relationship("MonthGoal", back_populates="user", cascade="all, delete-orphan")
    privacy_settings = relationship("PrivacySettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PrivacySettings(Base):
    __tablename__ = "privacy_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # General privacy
    profile_public = Column(Boolean, default=True, nullable=False)
    show_avatar = Column(Boolean, default=True, nullable=False)
    show_name = Column(Boolean, default=True, nullable=False)
    show_stats = Column(Boolean, default=True, nullable=False)
    
    # Graph visibility
    show_goal_chart = Column(Boolean, default=True, nullable=False)
    show_difficulty_chart = Column(Boolean, default=True, nullable=False)
    show_tasks_chart = Column(Boolean, default=True, nullable=False)
    show_xp_chart = Column(Boolean, default=True, nullable=False)
    show_cumulative_chart = Column(Boolean, default=True, nullable=False)
    show_streak_chart = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="privacy_settings")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SolvedTask(Base):
    __tablename__ = "solved_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for migration
    date = Column(Date, nullable=False, index=True)
    platform = Column(String(50), nullable=False, default="leetcode")
    problem_id = Column(String(50), nullable=True)
    title = Column(String(200), nullable=True)
    difficulty = Column(String(10), nullable=False)  # Easy / Medium / Hard
    points = Column(Integer, nullable=False)  # XP
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MonthGoal(Base):
    __tablename__ = "month_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for migration
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    target_xp = Column(Integer, nullable=False, default=100)
    
    # Relationships
    user = relationship("User", back_populates="month_goals")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
