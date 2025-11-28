"""
LeetCode Sync Router.

Synchronizes tasks from LeetCode to local database.
"""

from datetime import datetime, timezone
import logging
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from leetcode_tracker.database import get_db
from leetcode_tracker.dependencies import get_current_user
from leetcode_tracker.leetcode_client import get_leetcode_client
from leetcode_tracker.models import SolvedTask, User


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sync", tags=["sync"])


def get_difficulty_from_problem(_problem_title: str, _leetcode_username: str) -> str:
    """
    Get difficulty for a problem by fetching problem details.

    This is a fallback - ideally we'd cache this or get it from submissions.
    """
    # For now, return Medium as default since we can't easily get difficulty from submissions
    # In a real implementation, you'd want to:
    # 1. Cache problem difficulties
    # 2. Or fetch problem details for each unique problem
    return "Medium"


def calculate_xp(difficulty: str) -> int:
    """Calculate XP based on difficulty."""
    xp_map = {"Easy": 1, "Medium": 3, "Hard": 5}
    return xp_map.get(difficulty, 3)


async def sync_leetcode_submissions(user_id: int, leetcode_username: str, db: Session, limit: int = 100):
    """Background task to sync LeetCode submissions to database."""
    try:
        logger.info(f"Starting sync for user {user_id}, LeetCode username: {leetcode_username}")

        client = get_leetcode_client()

        # Fetch recent accepted submissions
        submissions = await client.get_recent_ac_submissions(leetcode_username, limit=limit)

        logger.info(f"Fetched {len(submissions)} submissions from LeetCode")

        synced_count = 0
        skipped_count = 0

        # Get problem details to determine difficulty
        # We'll need to fetch this for unique problems
        problem_difficulties = {}

        for submission in submissions:
            try:
                # Convert timestamp to date
                submission_date = datetime.fromtimestamp(int(submission["timestamp"]), tz=timezone.utc).date()
                title = submission["title"]
                title_slug = submission["titleSlug"]

                # Check if this task already exists
                existing = (
                    db.query(SolvedTask)
                    .filter(
                        SolvedTask.user_id == user_id, SolvedTask.title == title, SolvedTask.date == submission_date
                    )
                    .first()
                )

                if existing:
                    skipped_count += 1
                    continue

                # Get difficulty for this problem (cache it)
                if title_slug not in problem_difficulties:
                    try:
                        problem_details = await client.get_problem_details(title_slug)
                        difficulty = problem_details.get("difficulty", "Medium")
                        problem_difficulties[title_slug] = difficulty
                    except Exception as e:
                        logger.warning(f"Could not fetch difficulty for {title_slug}: {e}")
                        difficulty = "Medium"  # Default
                        problem_difficulties[title_slug] = difficulty
                else:
                    difficulty = problem_difficulties[title_slug]

                # Calculate XP
                points = calculate_xp(difficulty)

                # Create new task
                task = SolvedTask(
                    user_id=user_id,
                    date=submission_date,
                    title=title,
                    problem_id=submission.get("id"),
                    difficulty=difficulty,
                    points=points,
                    platform="leetcode",
                    notes=f"Synced from LeetCode (Language: {submission.get('lang', 'Unknown')})",
                )

                db.add(task)
                synced_count += 1

            except Exception as e:
                logger.error(f"Error processing submission {submission.get('title')}: {e}")
                continue

        # Commit all changes
        db.commit()

        logger.info(f"Sync completed: {synced_count} new tasks added, {skipped_count} skipped (already exist)")

        return {"synced": synced_count, "skipped": skipped_count, "total_fetched": len(submissions)}

    except Exception as e:
        logger.error(f"Error during sync: {e}")
        db.rollback()
        raise


@router.put("/leetcode-username")
async def set_leetcode_username(
    leetcode_username: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    """Set or update LeetCode username for the current user."""
    try:
        # Verify the username exists on LeetCode
        client = get_leetcode_client()
        profile = await client.get_user_profile(leetcode_username)

        if not profile:
            raise HTTPException(status_code=404, detail=f"LeetCode user '{leetcode_username}' not found")

        # Update user's LeetCode username
        current_user.leetcode_username = leetcode_username
        db.commit()

        return {"message": "LeetCode username updated successfully", "leetcode_username": leetcode_username}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting LeetCode username: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/from-leetcode")
async def sync_from_leetcode(
    background_tasks: BackgroundTasks,
    limit: int = 100,
    current_user: Annotated[User, Depends(get_current_user)] = None,
    db: Annotated[Session, Depends(get_db)] = None,
):
    """
    Sync tasks from LeetCode to local database.

    Fetches recent accepted submissions and adds them as tasks.
    """
    if not current_user.leetcode_username:
        raise HTTPException(
            status_code=400,
            detail="LeetCode username not set. Please set it first using PUT /api/sync/leetcode-username",
        )

    # Start background sync
    background_tasks.add_task(sync_leetcode_submissions, current_user.id, current_user.leetcode_username, db, limit)

    return {
        "message": "Sync started in background",
        "leetcode_username": current_user.leetcode_username,
        "limit": limit,
    }


@router.get("/status")
async def get_sync_status(
    current_user: Annotated[User, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]
):
    """Get sync status and LeetCode username."""
    # Get total tasks from LeetCode
    total_tasks = (
        db.query(SolvedTask).filter(SolvedTask.user_id == current_user.id, SolvedTask.platform == "leetcode").count()
    )

    return {
        "leetcode_username": current_user.leetcode_username,
        "has_leetcode_username": current_user.leetcode_username is not None,
        "total_leetcode_tasks": total_tasks,
    }
