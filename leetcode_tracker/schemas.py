from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# User schemas
class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    oauth_provider: str
    oauth_id: str
    avatar_url: Optional[str] = None


class User(UserBase):
    id: int
    oauth_provider: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# UserProfile schemas
class UserProfileBase(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    pass


class UserProfile(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# PrivacySettings schemas
class PrivacySettingsBase(BaseModel):
    profile_public: bool = True
    show_avatar: bool = True
    show_name: bool = True
    show_stats: bool = True
    show_goal_chart: bool = True
    show_difficulty_chart: bool = True
    show_tasks_chart: bool = True
    show_xp_chart: bool = True
    show_cumulative_chart: bool = True
    show_streak_chart: bool = True


class PrivacySettingsUpdate(PrivacySettingsBase):
    pass


class PrivacySettings(PrivacySettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Task schemas
class TaskBase(BaseModel):
    date: date
    platform: str = "leetcode"
    problem_id: Optional[str] = None
    title: Optional[str] = None
    difficulty: str  # "Easy" | "Medium" | "Hard"
    points: int
    time_spent: Optional[int] = None  # Time in minutes
    notes: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class DailyStat(BaseModel):
    date: date
    tasks_count: int
    xp_sum: int
    streak: int
    xp_cumulative: int


# MonthGoal schemas
class MonthGoalBase(BaseModel):
    year: int
    month: int
    target_xp: int = 100


class MonthGoalCreate(MonthGoalBase):
    pass


class MonthGoal(MonthGoalBase):
    id: int
    user_id: Optional[int] = None

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


# Rank system
class RankInfo(BaseModel):
    name: str
    min_xp: int
    icon: str
    color: str


# Leaderboard schemas
class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    show_avatar: bool = True
    show_name: bool = True
    xp: int
    tasks_count: int
    avg_xp_per_task: float


class Leaderboard(BaseModel):
    period: str  # 'day', 'week', 'month'
    entries: List[LeaderboardEntry]


# User stats for profile
class UserStats(BaseModel):
    user_id: int
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    show_avatar: bool = True
    show_name: bool = True
    show_stats: bool = True
    
    # Stats
    total_xp: int = 0
    total_tasks: int = 0
    easy_count: int = 0
    medium_count: int = 0
    hard_count: int = 0
    current_streak: int = 0
    avg_xp_per_task: float = 0.0
    
    # Rank
    rank_name: str
    rank_icon: str
    rank_color: str
    
    # Privacy
    privacy_settings: PrivacySettings
