from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from ..dependencies import templates, get_db, get_current_user, get_current_user_optional
from .. import models

router = APIRouter()

@router.get("/profile", response_class=HTMLResponse)
def profile_page(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User profile page."""
    # Calculate stats
    total_xp = db.query(func.sum(models.SolvedTask.points)).filter(models.SolvedTask.user_id == current_user.id).scalar() or 0
    total_tasks = db.query(func.count(models.SolvedTask.id)).filter(models.SolvedTask.user_id == current_user.id).scalar() or 0
    
    current_date = date.today()
    tasks_this_month = db.query(func.count(models.SolvedTask.id)).filter(
        models.SolvedTask.user_id == current_user.id,
        extract('month', models.SolvedTask.date) == current_date.month,
        extract('year', models.SolvedTask.date) == current_date.year
    ).scalar() or 0

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "current_user": current_user,
            "total_xp": total_xp,
            "total_tasks": total_tasks,
            "tasks_this_month": tasks_this_month
        },
    )

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
