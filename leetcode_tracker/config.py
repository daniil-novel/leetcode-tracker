"""Application configuration using Pydantic Settings."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_hours: int = 24 * 7  # 7 days
    
    # GitHub OAuth
    github_client_id: str
    github_client_secret: str
    github_redirect_uri: str = "https://novel-cloudtech.com:7443/auth/callback/github"
    
    # Google OAuth (optional)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./leetcode.db"
    
    # Application
    app_title: str = "LeetCode Tracker"
    debug: bool = False
    
    # Logging
    log_level: str = "INFO"
    
    # LeetCode Auto-Sync
    leetcode_sync_enabled: bool = True
    leetcode_sync_interval: int = 10  # seconds
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )


# Create global settings instance
settings = Settings()
