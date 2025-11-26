"""
User Profile Router
Handles user profile viewing and editing
"""

from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..leetcode_client import get_leetcode_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me")
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "leetcode_username": current_user.leetcode_username,
        "oauth_provider": current_user.oauth_provider,
        "created_at": current_user.created_at
    }


@router.put("/leetcode")
async def update_leetcode_settings(
    leetcode_username: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update LeetCode username for automatic synchronization
    Verifies that the username exists on LeetCode
    """
    try:
        # Verify the username exists on LeetCode
        client = get_leetcode_client()
        profile = await client.get_user_profile(leetcode_username)
        
        if not profile:
            raise HTTPException(
                status_code=404,
                detail=f"LeetCode user '{leetcode_username}' not found. Please check the username and make sure your profile is public."
            )
        
        # Update user's LeetCode username
        current_user.leetcode_username = leetcode_username
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"User {current_user.id} updated LeetCode username to {leetcode_username}")
        
        return {
            "success": True,
            "message": "LeetCode username updated successfully! Automatic synchronization will start within 10 seconds.",
            "leetcode_username": leetcode_username,
            "leetcode_profile": {
                "username": profile.get("username"),
                "ranking": profile.get("profile", {}).get("ranking"),
                "reputation": profile.get("profile", {}).get("reputation")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating LeetCode username: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error verifying LeetCode username: {str(e)}"
        )


@router.delete("/leetcode")
async def remove_leetcode_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove LeetCode username (stops automatic synchronization)"""
    current_user.leetcode_username = None
    db.commit()
    
    logger.info(f"User {current_user.id} removed LeetCode username")
    
    return {
        "success": True,
        "message": "LeetCode username removed. Automatic synchronization stopped."
    }
