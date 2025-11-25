from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi import Depends
from .database import get_db
from .auth import get_current_user, get_current_user_optional

# Setup Templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Re-export dependencies for convenience
__all__ = ["get_db", "get_current_user", "get_current_user_optional", "templates"]
