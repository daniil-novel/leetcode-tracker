import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# By default use SQLite in current working directory.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leetcode.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that provides a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
