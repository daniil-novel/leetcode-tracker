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

# Configure logging
logging.basicConfig(level=logging.INFO)
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
    logger.info(f"Adding task for user {current_user.id}: date={date_}, difficulty={difficulty}, points={points}")
    
    try:
        task_in = schemas.TaskCreate(
            date=date_,
            difficulty=difficulty,
            points=points,
            title=title or None,
            problem_id=problem_id or None,
            time_spent=time_spent if time_spent else None,
            notes=notes or None,
        )
        
        # Use model_dump() instead of dict() for Pydantic v2
        task_data = task_in.model_dump() if hasattr(task_in, 'model_dump') else task_in.dict()
        task = models.SolvedTask(**task_data, user_id=current_user.id)
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"Task {task.id} successfully added for user {current_user.id}")
        return RedirectResponse(url="/", status_code=303)
        
    except Exception as e:
        logger.error(f"Error adding task for user {current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add task: {str(e)}")


@router.get("/api/tasks", response_model=list[schemas.Task])
def api_tasks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return all tasks for current user."""
    logger.info(f"Fetching tasks for user {current_user.id}")
    
    try:
        tasks = (
            db.query(models.SolvedTask)
            .filter(models.SolvedTask.user_id == current_user.id)
            .order_by(models.SolvedTask.date.desc())
            .all()
        )
        logger.info(f"Found {len(tasks)} tasks for user {current_user.id}")
        return tasks
        
    except Exception as e:
        logger.error(f"Error fetching tasks for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch tasks: {str(e)}")


@router.delete("/api/task/{task_id}")
def delete_task(
    task_id: int, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a specific task."""
    logger.info(f"Deleting task {task_id} for user {current_user.id}")
    
    try:
        task = db.query(models.SolvedTask).filter(
            models.SolvedTask.id == task_id,
            models.SolvedTask.user_id == current_user.id
        ).first()
        
        if not task:
            logger.warning(f"Task {task_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Task not found or access denied")
        
        db.delete(task)
        db.commit()
        
        logger.info(f"Task {task_id} successfully deleted for user {current_user.id}")
        return {"message": "Task deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete task: {str(e)}")


@router.put("/api/task/{task_id}")
def update_task(
    task_id: int, 
    task_data: schemas.TaskCreate, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a specific task."""
    logger.info(f"Updating task {task_id} for user {current_user.id}")
    
    try:
        task = db.query(models.SolvedTask).filter(
            models.SolvedTask.id == task_id,
            models.SolvedTask.user_id == current_user.id
        ).first()
        
        if not task:
            logger.warning(f"Task {task_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Task not found or access denied")
        
        task.date = task_data.date
        task.difficulty = task_data.difficulty
        task.points = task_data.points
        task.title = task_data.title
        task.problem_id = task_data.problem_id
        task.notes = task_data.notes
        
        if hasattr(task_data, 'time_spent') and task_data.time_spent is not None:
            task.time_spent = task_data.time_spent
        
        db.commit()
        db.refresh(task)
        
        logger.info(f"Task {task_id} successfully updated for user {current_user.id}")
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update task: {str(e)}")


@router.delete("/api/tasks/clear")
def clear_all_tasks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all tasks for current user."""
    logger.info(f"Clearing all tasks for user {current_user.id}")
    
    try:
        deleted_count = db.query(models.SolvedTask).filter(
            models.SolvedTask.user_id == current_user.id
        ).delete()
        db.commit()
        
        logger.info(f"Successfully deleted {deleted_count} tasks for user {current_user.id}")
        return {"deleted": deleted_count, "message": f"Successfully deleted {deleted_count} tasks"}
        
    except Exception as e:
        logger.error(f"Error clearing tasks for user {current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to clear tasks: {str(e)}")


@router.post("/api/import/csv")
async def import_csv_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import tasks from uploaded CSV file."""
    logger.info(f"Starting CSV import for user {current_user.id}, file: {file.filename}")
    
    try:
        # Read file content
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")
        
        # Try different encodings
        text_content = None
        used_encoding = None
        for encoding in ['utf-8', 'cp1251', 'windows-1251', 'iso-8859-1']:
            try:
                text_content = content.decode(encoding)
                used_encoding = encoding
                logger.info(f"Successfully decoded file using {encoding}")
                break
            except UnicodeDecodeError:
                logger.debug(f"Failed to decode with {encoding}")
                continue
        
        if text_content is None:
            logger.error("Failed to decode file with any encoding")
            return JSONResponse(
                status_code=400,
                content={"error": "Не удалось прочитать файл. Попробуйте сохранить файл в кодировке UTF-8"}
            )
        
        # Parse CSV
        csv_file = io.StringIO(text_content)
        reader = csv.DictReader(csv_file)
        
        # Log CSV headers
        if reader.fieldnames:
            logger.info(f"CSV headers: {reader.fieldnames}")
        
        imported_count = 0
        errors = []
        
        for row_num, row in enumerate(reader, start=2):
            try:
                logger.debug(f"Processing row {row_num}: {row}")
                
                # Check if it's aggregate format (easy/medium/hard columns)
                if 'easy' in row or 'medium' in row or 'hard' in row:
                    logger.debug(f"Row {row_num}: Using aggregate format")
                    task_date = date.fromisoformat(row['date'])
                    
                    # Import Easy tasks
                    easy_count = int(row.get('easy', 0) or 0)
                    for i in range(easy_count):
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
                    
                    # Import Medium tasks
                    medium_count = int(row.get('medium', 0) or 0)
                    for i in range(medium_count):
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
                    
                    # Import Hard tasks
                    hard_count = int(row.get('hard', 0) or 0)
                    for i in range(hard_count):
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
                    
                    logger.debug(f"Row {row_num}: Imported {easy_count} Easy, {medium_count} Medium, {hard_count} Hard tasks")
                
                else:
                    # Individual task format
                    logger.debug(f"Row {row_num}: Using individual task format")
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
                    logger.debug(f"Row {row_num}: Imported 1 {difficulty} task")
                    
            except Exception as e:
                error_msg = f"Строка {row_num}: {str(e)}"
                errors.append(error_msg)
                logger.error(f"Error processing row {row_num}: {str(e)}", exc_info=True)
        
        # Commit all changes
        db.commit()
        logger.info(f"CSV import completed: {imported_count} tasks imported, {len(errors)} errors")
        
        message = f"Успешно импортировано {imported_count} задач"
        if errors:
            message += f"\n\nОшибки:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n... и еще {len(errors) - 5} ошибок"
        
        return {"imported": imported_count, "message": message, "errors": errors if errors else None}
        
    except Exception as e:
        logger.error(f"CSV import failed for user {current_user.id}: {str(e)}", exc_info=True)
        db.rollback()
        return JSONResponse(
            status_code=400,
            content={"error": f"Ошибка импорта: {str(e)}"}
        )
