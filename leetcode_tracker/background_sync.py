"""
Background LeetCode Synchronization Service.

Automatically syncs LeetCode data for all users every 10 seconds.
"""

import asyncio
import contextlib
from datetime import datetime, timezone
from functools import lru_cache
import logging

from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .leetcode_client import get_leetcode_client
from .models import SolvedTask, User


logger = logging.getLogger(__name__)


class LeetCodeSyncService:
    """Background service for continuous LeetCode synchronization."""

    def __init__(self, sync_interval: int = 10) -> None:
        """
        Initialize sync service.

        Args:
            sync_interval: Interval in seconds between syncs (default: 10)

        """
        self.sync_interval = sync_interval
        self.is_running = False
        self._task = None

    async def start(self) -> None:
        """Start the background sync service."""
        if self.is_running:
            logger.warning("Sync service is already running")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._sync_loop())
        logger.info(f"🔄 LeetCode sync service started (interval: {self.sync_interval}s)")

    async def stop(self) -> None:
        """Stop the background sync service."""
        if not self.is_running:
            return

        self.is_running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        logger.info("🛑 LeetCode sync service stopped")

    async def _sync_loop(self) -> None:
        """Run the main sync loop."""
        while self.is_running:
            try:
                await self._sync_all_users()
            except Exception as e:
                logger.error(f"Error in sync loop: {e}", exc_info=True)

            # Wait for next sync interval
            await asyncio.sleep(self.sync_interval)

    async def _sync_all_users(self) -> None:
        """Sync LeetCode data for all users with leetcode_username set."""
        db = SessionLocal()
        try:
            # Get all users with LeetCode username
            users = db.query(User).filter(User.leetcode_username.isnot(None)).all()

            if not users:
                logger.debug("No users with LeetCode username to sync")
                return

            logger.info(f"Syncing {len(users)} users...")

            for user in users:
                try:
                    await self._sync_user(user, db)
                except Exception as e:
                    logger.error(f"Error syncing user {user.id} ({user.leetcode_username}): {e}")
                    continue

            logger.info(f"✅ Sync completed for {len(users)} users")

        finally:
            db.close()

    async def _sync_user(self, user: User, db: Session) -> None:
        """
        Sync LeetCode data for a single user.

        Args:
            user: User object
            db: Database session

        """
        if not user.leetcode_username:
            return

        try:
            client = get_leetcode_client()

            # Fetch recent accepted submissions (last 20 to avoid rate limits)
            submissions = await client.get_recent_ac_submissions(user.leetcode_username, limit=20)

            if not submissions:
                logger.debug(f"No submissions found for {user.leetcode_username}")
                return

            synced_count = 0
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
                            SolvedTask.user_id == user.id, SolvedTask.title == title, SolvedTask.date == submission_date
                        )
                        .first()
                    )

                    if existing:
                        continue

                    # Get difficulty for this problem (cache it)
                    if title_slug not in problem_difficulties:
                        try:
                            problem_details = await client.get_problem_details(title_slug)
                            difficulty = problem_details.get("difficulty", "Medium")
                            problem_difficulties[title_slug] = difficulty
                        except Exception as e:
                            logger.warning(f"Could not fetch difficulty for {title_slug}: {e}")
                            difficulty = "Medium"
                            problem_difficulties[title_slug] = difficulty
                    else:
                        difficulty = problem_difficulties[title_slug]

                    # Calculate XP
                    xp_map = {"Easy": 1, "Medium": 3, "Hard": 5}
                    points = xp_map.get(difficulty, 3)

                    # Create new task
                    task = SolvedTask(
                        user_id=user.id,
                        date=submission_date,
                        title=title,
                        problem_id=submission.get("id"),
                        difficulty=difficulty,
                        points=points,
                        platform="leetcode",
                        notes=f"Auto-synced from LeetCode (Language: {submission.get('lang', 'Unknown')})",
                    )

                    db.add(task)
                    synced_count += 1

                except Exception as e:
                    logger.error(f"Error processing submission {submission.get('title')}: {e}")
                    continue

            if synced_count > 0:
                db.commit()
                logger.info(f"✅ Synced {synced_count} new tasks for user {user.leetcode_username}")

        except Exception as e:
            logger.error(f"Error syncing user {user.leetcode_username}: {e}")
            db.rollback()
            raise


@lru_cache(maxsize=1)
def get_sync_service() -> LeetCodeSyncService:
    """Get or create the global sync service instance."""
    return LeetCodeSyncService(sync_interval=settings.leetcode_sync_interval)


async def start_sync_service() -> None:
    """Start the background sync service."""
    if not settings.leetcode_sync_enabled:
        logger.info("LeetCode auto-sync is disabled in settings")
        return

    service = get_sync_service()
    await service.start()


async def stop_sync_service() -> None:
    """Stop the background sync service."""
    service = get_sync_service()
    await service.stop()
