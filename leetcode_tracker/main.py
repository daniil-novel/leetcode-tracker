from __future__ import annotations

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional
from collections import defaultdict
import calendar

from fastapi import FastAPI, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import csv
import io
import httpx
import os

from .database import Base, engine, get_db
from . import models, schemas
from .auth import (
    oauth, 
    create_access_token, 
    get_current_user, 
    get_current_user_optional,
    get_or_create_user
)

# Create DB tables on startup (simple dev approach)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LeetCode Tracker")

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
)

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# ============== Authentication Endpoints ==============

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/auth/github")
async def auth_github(request: Request):
    """Redirect to GitHub OAuth."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("GitHub OAuth: Starting authorization")
        redirect_uri = request.url_for('auth_callback_github')
        logger.info(f"Redirect URI: {redirect_uri}")
        
        result = await oauth.github.authorize_redirect(request, redirect_uri)
        logger.info("GitHub OAuth: Redirect created successfully")
        return result
        
    except Exception as e:
        logger.error(f"GitHub OAuth ERROR: {str(e)}")
        return RedirectResponse(url=f"/login?error={str(e)}", status_code=303)


@app.get("/auth/callback/github")
async def auth_callback_github(request: Request, db: Session = Depends(get_db)):
    """GitHub OAuth callback."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("GitHub OAuth Callback: Started")
        
        token = await oauth.github.authorize_access_token(request)
        logger.info("GitHub OAuth: Token received")
        
        # Get user info from GitHub
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            user_data = resp.json()
            
        logger.info(f"GitHub user data: {user_data.get('login', 'UNKNOWN')}")
        
        # Get or create user
        user = get_or_create_user(
            oauth_provider="github",
            oauth_id=str(user_data['id']),
            email=user_data.get('email'),
            username=user_data['login'],
            avatar_url=user_data.get('avatar_url'),
            db=db
        )
        
        logger.info(f"User created/found: {user.username} (ID: {user.id})")
        
        # Create access token
        access_token = create_access_token(data={"sub": user.id})
        logger.info("JWT token created successfully")
        
        # Redirect to home with token in URL
        response = RedirectResponse(url=f"/?token={access_token}", status_code=303)
        logger.info("GitHub OAuth: Success! Redirecting to home")
        return response
        
    except Exception as e:
        logger.error(f"GitHub OAuth Callback ERROR: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return RedirectResponse(url=f"/login?error={str(e)}", status_code=303)


# ============== Main Pages ==============

@app.get("/", response_class=HTMLResponse)
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


# ============== Task Endpoints ==============

@app.post("/add")
def add_task(
    request: Request,
    date_: date = Form(..., alias="date"),
    difficulty: str = Form(...),
    points: int = Form(...),
    title: str = Form(""),
    problem_id: str = Form(""),
    notes: str = Form(""),
    current_user: models.User = Depends(get_current_user),
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
    task = models.SolvedTask(**task_in.dict(), user_id=current_user.id)
    db.add(task)
    db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.get("/api/tasks", response_model=list[schemas.Task])
def api_tasks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return all tasks for current user."""
    tasks = (
        db.query(models.SolvedTask)
        .filter(models.SolvedTask.user_id == current_user.id)
        .order_by(models.SolvedTask.date.asc())
        .all()
    )
    return tasks


@app.delete("/api/task/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific task."""
    task = db.query(models.SolvedTask).filter(
        models.SolvedTask.id == task_id,
        models.SolvedTask.user_id == current_user.id
    ).first()
    
    if not task:
        return {"error": "Task not found"}, 404
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@app.put("/api/task/{task_id}")
def update_task(
    task_id: int,
    task_data: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific task."""
    task = db.query(models.SolvedTask).filter(
        models.SolvedTask.id == task_id,
        models.SolvedTask.user_id == current_user.id
    ).first()
    
    if not task:
        return {"error": "Task not found"}, 404
    
    task.date = task_data.date
    task.difficulty = task_data.difficulty
    task.points = task_data.points
    task.title = task_data.title
    task.problem_id = task_data.problem_id
    task.notes = task_data.notes
    
    db.commit()
    db.refresh(task)
    return task


@app.delete("/api/tasks/clear")
def clear_all_tasks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all tasks for current user."""
    deleted_count = db.query(models.SolvedTask).filter(
        models.SolvedTask.user_id == current_user.id
    ).delete()
    db.commit()
    return {"deleted": deleted_count, "message": f"Successfully deleted {deleted_count} tasks"}


# ============== Stats Endpoints ==============

@app.get("/api/stats/daily", response_model=list[schemas.DailyStat])
def api_daily_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aggregate stats per day for current user."""
    rows = (
        db.query(models.SolvedTask.date)
        .filter(models.SolvedTask.user_id == current_user.id)
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

    count_by_date: dict[date, int] = defaultdict(int)
    xp_by_date: dict[date, int] = defaultdict(int)

    tasks = db.query(models.SolvedTask).filter(
        models.SolvedTask.user_id == current_user.id
    ).all()
    
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


# ============== Month Goal Endpoints ==============

@app.get("/api/month/goal/{year}/{month}", response_model=schemas.MonthGoal)
def get_month_goal(
    year: int,
    month: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get or create month goal for current user."""
    goal = (
        db.query(models.MonthGoal)
        .filter(
            models.MonthGoal.user_id == current_user.id,
            models.MonthGoal.year == year,
            models.MonthGoal.month == month
        )
        .first()
    )
    
    if not goal:
        goal = models.MonthGoal(
            user_id=current_user.id,
            year=year,
            month=month,
            target_xp=100
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
    
    return goal


@app.post("/api/month/goal")
def set_month_goal(
    goal_data: schemas.MonthGoalCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set month goal for current user."""
    existing = (
        db.query(models.MonthGoal)
        .filter(
            models.MonthGoal.user_id == current_user.id,
            models.MonthGoal.year == goal_data.year,
            models.MonthGoal.month == goal_data.month
        )
        .first()
    )
    
    if existing:
        existing.target_xp = goal_data.target_xp
        db.commit()
        db.refresh(existing)
        return existing
    else:
        goal = models.MonthGoal(
            **goal_data.dict(),
            user_id=current_user.id
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal


@app.get("/api/month/stats/{year}/{month}", response_model=schemas.MonthStats)
def get_month_stats(
    year: int,
    month: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get complete month statistics for current user."""
    # Get or create goal
    goal = (
        db.query(models.MonthGoal)
        .filter(
            models.MonthGoal.user_id == current_user.id,
            models.MonthGoal.year == year,
            models.MonthGoal.month == month
        )
        .first()
    )
    
    if not goal:
        goal = models.MonthGoal(
            user_id=current_user.id,
            year=year,
            month=month,
            target_xp=100
        )
        db.add(goal)
        db.commit()
    
    # Get all tasks for this month
    tasks = (
        db.query(models.SolvedTask)
        .filter(
            models.SolvedTask.user_id == current_user.id,
            extract('year', models.SolvedTask.date) == year,
            extract('month', models.SolvedTask.date) == month
        )
        .order_by(models.SolvedTask.date.asc())
        .all()
    )
    
    # Calculate stats
    total_xp = sum(t.points for t in tasks)
    total_tasks = len(tasks)
    easy_count = len([t for t in tasks if t.difficulty == 'Easy'])
    medium_count = len([t for t in tasks if t.difficulty == 'Medium'])
    hard_count = len([t for t in tasks if t.difficulty == 'Hard'])
    progress = (total_xp / goal.target_xp * 100) if goal.target_xp > 0 else 0
    
    # Build calendar
    _, num_days = calendar.monthrange(year, month)
    calendar_days = []
    
    # Group tasks by date
    tasks_by_date = defaultdict(list)
    for task in tasks:
        tasks_by_date[task.date].append(task)
    
    # Create calendar days
    for day in range(1, num_days + 1):
        day_date = date(year, month, day)
        day_tasks = tasks_by_date.get(day_date, [])
        
        day_xp = sum(t.points for t in day_tasks)
        day_easy = len([t for t in day_tasks if t.difficulty == 'Easy'])
        day_medium = len([t for t in day_tasks if t.difficulty == 'Medium'])
        day_hard = len([t for t in day_tasks if t.difficulty == 'Hard'])
        
        calendar_days.append(schemas.CalendarDay(
            date=day_date,
            tasks_count=len(day_tasks),
            xp_sum=day_xp,
            easy_count=day_easy,
            medium_count=day_medium,
            hard_count=day_hard,
            tasks=day_tasks
        ))
    
    return schemas.MonthStats(
        year=year,
        month=month,
        target_xp=goal.target_xp,
        current_xp=total_xp,
        total_tasks=total_tasks,
        easy_count=easy_count,
        medium_count=medium_count,
        hard_count=hard_count,
        progress_percent=progress,
        calendar_days=calendar_days
    )


# ============== CSV Import ==============

@app.post("/api/import/csv")
async def import_csv_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import tasks from uploaded CSV file."""
    try:
        content = await file.read()
        
        text_content = None
        for encoding in ['utf-8', 'cp1251', 'windows-1251', 'iso-8859-1']:
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if text_content is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Не удалось прочитать файл. Попробуйте сохранить файл в кодировке UTF-8"}
            )
        
        csv_file = io.StringIO(text_content)
        reader = csv.DictReader(csv_file)
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                if 'easy' in row or 'medium' in row or 'hard' in row:
                    task_date = date.fromisoformat(row['date'])
                    
                    for i in range(int(row.get('easy', 0) or 0)):
                        task = models.SolvedTask(
                            user_id=current_user.id,
                            date=task_date,
                            difficulty="Easy",
                            points=1,
                            title=row.get('title', f"Imported Easy task {i+1}") if 'title' in row else f"Imported Easy task {i+1}",
                            notes="Imported from CSV"
                        )
                        db.add(task)
                        imported_count += 1
                    
                    for i in range(int(row.get('medium', 0) or 0)):
                        task = models.SolvedTask(
                            user_id=current_user.id,
                            date=task_date,
                            difficulty="Medium",
                            points=3,
                            title=row.get('title', f"Imported Medium task {i+1}") if 'title' in row else f"Imported Medium task {i+1}",
                            notes="Imported from CSV"
                        )
                        db.add(task)
                        imported_count += 1
                    
                    for i in range(int(row.get('hard', 0) or 0)):
                        task = models.SolvedTask(
                            user_id=current_user.id,
                            date=task_date,
                            difficulty="Hard",
                            points=5,
                            title=row.get('title', f"Imported Hard task {i+1}") if 'title' in row else f"Imported Hard task {i+1}",
                            notes="Imported from CSV"
                        )
                        db.add(task)
                        imported_count += 1
                
                else:
                    task_date = date.fromisoformat(row['date'])
                    difficulty = row.get('difficulty', 'Medium')
                    
                    if 'points' in row and row['points']:
                        points = int(row['points'])
                    else:
                        points = {'Easy': 1, 'Medium': 3, 'Hard': 5}.get(difficulty, 3)
                    
                    task = models.SolvedTask(
                        user_id=current_user.id,
                        date=task_date,
                        difficulty=difficulty,
                        points=points,
                        title=row.get('title', None) or None,
                        problem_id=row.get('problem_id', None) or None,
                        notes=row.get('notes', "Imported from CSV") or "Imported from CSV"
                    )
                    db.add(task)
                    imported_count += 1
                    
            except Exception as e:
                errors.append(f"Строка {row_num}: {str(e)}")
        
        db.commit()
        
        message = f"Успешно импортировано {imported_count} задач"
        if errors:
            message += f"\n\nОшибки:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n... и еще {len(errors) - 5} ошибок"
        
        return {"imported": imported_count, "message": message, "errors": errors if errors else None}
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Ошибка импорта: {str(e)}"}
        )


@app.get("/logout")
def logout():
    """Logout endpoint."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("Authorization") # Consider removing other session cookies or local storage items if used
    return response
