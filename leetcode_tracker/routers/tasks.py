import csv
import io
import logging
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException, Response
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models, schemas
from ..dependencies import get_db, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/add")
def add_task(
    request: Request,
    date_: date = Form(..., alias="date"),
    difficulty: str = Form(...),
    points: int = Form(...),
    title: str = Form(""),
    problem_id: str = Form(""),
    time_spent: int = Form(None),
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
        time_spent=time_spent if time_spent else None,
        notes=notes or None,
    )
    task = models.SolvedTask(**task_in.dict(), user_id=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task) # Refresh to get task.id etc.

    return RedirectResponse(url="/", status_code=303)


@router.get("/api/tasks", response_model=list[schemas.Task])
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


@router.delete("/api/task/{task_id}")
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
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


@router.put("/api/task/{task_id}")
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
        raise HTTPException(status_code=404, detail="Task not found or access denied")
    
    task.date = task_data.date
    task.difficulty = task_data.difficulty
    task.points = task_data.points
    task.title = task_data.title
    task.problem_id = task_data.problem_id
    task.notes = task_data.notes
    # Assuming TaskCreate includes time_spent
    if hasattr(task_data, 'time_spent') and task_data.time_spent is not None:
        task.time_spent = task_data.time_spent
    # Else: if not provided and it was previously set, should it be nullified or kept?
    # For now, it keeps its old value if not explicitly passed (depends on schema.TaskCreate defaults too)
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/api/tasks/clear")
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


@router.post("/api/import/csv")
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
