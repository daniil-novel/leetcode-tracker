"""
LeetCode API Router
Provides endpoints to fetch data directly from LeetCode
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from ..leetcode_client import get_leetcode_client, LeetCodeClient
from ..dependencies import get_current_user
from ..models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leetcode", tags=["leetcode"])


@router.get("/{username}/profile")
async def get_leetcode_profile(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user profile information"""
    try:
        client = get_leetcode_client()
        profile = await client.get_user_profile(username)
        
        if not profile:
            raise HTTPException(status_code=404, detail=f"LeetCode user '{username}' not found")
        
        return profile
    except Exception as e:
        logger.error(f"Error fetching LeetCode profile for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/solved")
async def get_leetcode_solved(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's solved problems statistics"""
    try:
        client = get_leetcode_client()
        solved = await client.get_user_solved_problems(username)
        return solved
    except Exception as e:
        logger.error(f"Error fetching solved problems for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/calendar")
async def get_leetcode_calendar(
    username: str,
    year: Optional[int] = Query(None, description="Year for calendar data"),
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's submission calendar"""
    try:
        client = get_leetcode_client()
        calendar = await client.get_user_calendar(username, year)
        return calendar
    except Exception as e:
        logger.error(f"Error fetching calendar for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/submissions")
async def get_leetcode_submissions(
    username: str,
    limit: int = Query(20, ge=1, le=100, description="Number of submissions to fetch"),
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's recent submissions"""
    try:
        client = get_leetcode_client()
        submissions = await client.get_recent_submissions(username, limit)
        return {"submissions": submissions, "count": len(submissions)}
    except Exception as e:
        logger.error(f"Error fetching submissions for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/ac-submissions")
async def get_leetcode_ac_submissions(
    username: str,
    limit: int = Query(20, ge=1, le=100, description="Number of accepted submissions to fetch"),
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's recent accepted submissions"""
    try:
        client = get_leetcode_client()
        submissions = await client.get_recent_ac_submissions(username, limit)
        return {"submissions": submissions, "count": len(submissions)}
    except Exception as e:
        logger.error(f"Error fetching accepted submissions for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/contest")
async def get_leetcode_contest(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's contest information and history"""
    try:
        client = get_leetcode_client()
        contest_info = await client.get_user_contest_info(username)
        return contest_info
    except Exception as e:
        logger.error(f"Error fetching contest info for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/badges")
async def get_leetcode_badges(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's badges"""
    try:
        client = get_leetcode_client()
        badges = await client.get_user_badges(username)
        return badges
    except Exception as e:
        logger.error(f"Error fetching badges for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/language-stats")
async def get_leetcode_language_stats(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's programming language statistics"""
    try:
        client = get_leetcode_client()
        lang_stats = await client.get_user_language_stats(username)
        return {"languageStats": lang_stats}
    except Exception as e:
        logger.error(f"Error fetching language stats for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/skill-stats")
async def get_leetcode_skill_stats(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Get LeetCode user's skill statistics"""
    try:
        client = get_leetcode_client()
        skill_stats = await client.get_user_skill_stats(username)
        return skill_stats
    except Exception as e:
        logger.error(f"Error fetching skill stats for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily-problem")
async def get_daily_problem(
    current_user: User = Depends(get_current_user)
):
    """Get today's LeetCode daily coding challenge"""
    try:
        client = get_leetcode_client()
        daily = await client.get_daily_problem()
        return daily
    except Exception as e:
        logger.error(f"Error fetching daily problem: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/problem/{title_slug}")
async def get_problem_details(
    title_slug: str,
    current_user: User = Depends(get_current_user)
):
    """Get details about a specific LeetCode problem"""
    try:
        client = get_leetcode_client()
        problem = await client.get_problem_details(title_slug)
        
        if not problem:
            raise HTTPException(status_code=404, detail=f"Problem '{title_slug}' not found")
        
        return problem
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching problem {title_slug}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/problems")
async def get_problems_list(
    limit: int = Query(20, ge=1, le=100, description="Number of problems to fetch"),
    skip: int = Query(0, ge=0, description="Number of problems to skip"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty: EASY, MEDIUM, HARD"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    current_user: User = Depends(get_current_user)
):
    """Get list of LeetCode problems with optional filters"""
    try:
        client = get_leetcode_client()
        
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",")]
        
        problems = await client.get_problems_list(
            limit=limit,
            skip=skip,
            difficulty=difficulty,
            tags=tag_list
        )
        
        return problems
    except Exception as e:
        logger.error(f"Error fetching problems list: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{username}/sync")
async def sync_leetcode_data(
    username: str,
    current_user: User = Depends(get_current_user)
):
    """
    Sync all LeetCode data for a user in one call
    Returns profile, solved stats, calendar, and recent submissions
    """
    try:
        client = get_leetcode_client()
        
        # Fetch all data concurrently would be better, but for simplicity doing sequentially
        profile = await client.get_user_profile(username)
        solved = await client.get_user_solved_problems(username)
        calendar = await client.get_user_calendar(username)
        submissions = await client.get_recent_ac_submissions(username, limit=20)
        
        return {
            "username": username,
            "profile": profile,
            "solved": solved,
            "calendar": calendar,
            "recentSubmissions": submissions
        }
    except Exception as e:
        logger.error(f"Error syncing LeetCode data for {username}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
