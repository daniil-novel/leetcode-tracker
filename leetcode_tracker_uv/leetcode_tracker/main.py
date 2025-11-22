from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import List

from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas


# Create DB tables on startup (simple dev approach)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LeetCode Tracker")

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    """Main page with form, table and charts."""
    tasks = (
        db.query(models.SolvedTask)
        .order_by(models.SolvedTask.date.desc(), models.SolvedTask.id.desc())
        .limit(100)
        .all()
    )
    today = date.today()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "tasks": tasks,
            "today": today,
        },
    )


@app.post("/add")
def add_task(
    request: Request,
    date_: date = Form(..., alias="date"),
    difficulty: str = Form(...),
    points: int = Form(...),
    title: str = Form(""),
    problem_id: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    """Handle form submission and create a new task."""
    task_in = schemas.TaskCreate(
        date=date_,
        difficulty=difficulty,
        points=points,
        title=title or None,
        problem_id=problem_id or None,
        notes=notes or None,
    )
    task = models.SolvedTask(**task_in.dict())
    db.add(task)
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.get("/api/tasks", response_model=list[schemas.Task])
def api_tasks(db: Session = Depends(get_db)):
    """Return all tasks (for potential future use)."""
    tasks = db.query(models.SolvedTask).order_by(models.SolvedTask.date.asc()).all()
    return tasks


@app.get("/api/stats/daily", response_model=list[schemas.DailyStat])
def api_daily_stats(db: Session = Depends(get_db)):
    """Aggregate stats per day: tasks, xp, streak, cumulative xp."""
    rows = (
        db.query(models.SolvedTask.date)
        .distinct()
        .order_by(models.SolvedTask.date.asc())
        .all()
    )

    if not rows:
        return []

    all_dates: list[date] = []
    cur = rows[0][0]
    last = rows[-1][0]
    while cur <= last:
        all_dates.append(cur)
        cur = cur + timedelta(days=1)

    from collections import defaultdict

    count_by_date: dict[date, int] = defaultdict(int)
    xp_by_date: dict[date, int] = defaultdict(int)

    tasks = db.query(models.SolvedTask).all()
    for t in tasks:
        count_by_date[t.date] += 1
        xp_by_date[t.date] += t.points

    stats: list[schemas.DailyStat] = []
    streak = 0
    xp_cum = 0
    for d in all_dates:
        tasks_count = count_by_date[d]
        xp_sum = xp_by_date[d]
        if tasks_count > 0:
            streak += 1
        else:
            streak = 0
        xp_cum += xp_sum
        stats.append(
            schemas.DailyStat(
                date=d,
                tasks_count=tasks_count,
                xp_sum=xp_sum,
                streak=streak,
                xp_cumulative=xp_cum,
            )
        )

    return stats
