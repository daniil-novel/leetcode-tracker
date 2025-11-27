from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from ..dependencies import templates, get_db, get_current_user, get_current_user_optional
from .. import models

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    current_user: Optional[models.User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """Main page with form, table and charts."""
    tasks = []
    today = date.today()
    
    if current_user:
        tasks = (
            db.query(models.SolvedTask)
            .filter(models.SolvedTask.user_id == current_user.id)
            .order_by(models.SolvedTask.date.desc(), models.SolvedTask.id.desc())
            .limit(100)
            .all()
        )
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tasks": tasks,
            "today": today,
            "current_user": current_user,
        },
    )
