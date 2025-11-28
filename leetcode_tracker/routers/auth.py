import logging
import traceback
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session

from leetcode_tracker import models
from leetcode_tracker.auth import create_access_token, get_current_user, get_or_create_user, oauth
from leetcode_tracker.config import settings
from leetcode_tracker.dependencies import get_db


logger = logging.getLogger(__name__)

router = APIRouter()

# Remove the /login route - it's handled by React SPA routing
# The catch-all route in main.py will serve the React app for /login


@router.get("/api/auth/me")
async def get_current_user_info(current_user: Annotated[models.User, Depends(get_current_user)]):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "oauth_provider": current_user.oauth_provider,
    }


@router.get("/auth/github")
async def auth_github(request: Request):
    """Redirect to GitHub OAuth."""
    try:
        # Use configured redirect_uri to avoid mismatches/port issues
        # If not configured (empty), fallback to dynamic url_for
        if hasattr(settings, "github_redirect_uri") and settings.github_redirect_uri:
            redirect_uri = settings.github_redirect_uri
        else:
            redirect_uri = request.url_for("auth_callback_github")

        return await oauth.github.authorize_redirect(request, str(redirect_uri))

    except Exception as e:
        logger.error(f"GitHub OAuth ERROR (auth_github): {e!s}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return RedirectResponse(url=f"/login?error={e!s}", status_code=303)


@router.get("/auth/callback/github")
async def auth_callback_github(request: Request, db: Annotated[Session, Depends(get_db)]):
    """GitHub OAuth callback."""
    try:
        token = await oauth.github.authorize_access_token(request)

        # Get user info from GitHub
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.github.com/user", headers={"Authorization": f"Bearer {token['access_token']}"}
            )
            resp.raise_for_status()
            user_data = resp.json()

        logger.info(f"GitHub user authenticated: {user_data.get('login', 'UNKNOWN')}")

        # Get or create user
        user = get_or_create_user(
            oauth_provider="github",
            oauth_id=str(user_data["id"]),
            email=user_data.get("email"),
            username=user_data["login"],
            avatar_url=user_data.get("avatar_url"),
            db=db,
        )

        # Create access token
        access_token = create_access_token(data={"sub": user.id})

        # Create redirect response with token in URL for frontend
        # This allows the React frontend to extract the token and store it
        response = RedirectResponse(url=f"/login?token={access_token}", status_code=303)

        # Set persistent secure cookie (optional, but good for backup)
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=60 * 60 * 24 * 7,  # 7 days
            secure=True,
            samesite="lax",
            path="/",
        )

        logger.info(f"Auth successful for {user.username}, redirecting with token")
        return response

    except HTTPException:
        logger.error(f"GitHub OAuth Callback HTTP Exception: {traceback.format_exc()}")
        return RedirectResponse(url="/login?error=mismatching_state_or_auth_error", status_code=303)
    except Exception as e:
        logger.error(f"GitHub OAuth Callback ERROR: {e!s}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return RedirectResponse(url=f"/login?error={e!s}", status_code=303)


@router.get("/logout")
def logout():
    """Logout endpoint."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("Authorization", path="/")
    response.delete_cookie("session", path="/")  # Also clear authlib session
    return response
