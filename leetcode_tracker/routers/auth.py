import logging
import traceback
import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..dependencies import templates, get_db
from ..auth import oauth, create_access_token, get_or_create_user

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/auth/github")
async def auth_github(request: Request):
    """Redirect to GitHub OAuth."""
    try:
        # We can now use url_for because we trust proxy headers (configured in main.py)
        # This ensures protocol (https) and port are correct if headers are passed correctly.
        # Fallback to absolute URL if needed, but let's try dynamic first.
        redirect_uri = request.url_for('auth_callback_github')
        return await oauth.github.authorize_redirect(request, str(redirect_uri))
        
    except Exception as e:
        logger.error(f"GitHub OAuth ERROR (auth_github): {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return RedirectResponse(url=f"/login?error={str(e)}", status_code=303)


@router.get("/auth/callback/github")
async def auth_callback_github(request: Request, db: Session = Depends(get_db)):
    """GitHub OAuth callback."""
    try:
        token = await oauth.github.authorize_access_token(request)
        
        # Get user info from GitHub
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                'https://api.github.com/user',
                headers={'Authorization': f'Bearer {token["access_token"]}'}
            )
            resp.raise_for_status()
            user_data = resp.json()
        
        logger.info(f"GitHub user authenticated: {user_data.get('login', 'UNKNOWN')}")
        
        # Get or create user
        user = get_or_create_user(
            oauth_provider="github",
            oauth_id=str(user_data['id']),
            email=user_data.get('email'),
            username=user_data['login'],
            avatar_url=user_data.get('avatar_url'),
            db=db
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": user.id})
        
        # Create redirect response
        response = RedirectResponse(url="/", status_code=303)
        
        # Set persistent secure cookie
        response.set_cookie(
            key="Authorization",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=60 * 60 * 24 * 7, # 7 days
            secure=True, 
            samesite="lax",
            path="/"
        )
        
        logger.info(f"Auth successful for {user.username}, setting cookie")
        return response
        
    except HTTPException:
        logger.error(f"GitHub OAuth Callback HTTP Exception: {traceback.format_exc()}")
        return RedirectResponse(url=f"/login?error=mismatching_state_or_auth_error", status_code=303)
    except Exception as e:
        logger.error(f"GitHub OAuth Callback ERROR: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return RedirectResponse(url=f"/login?error={str(e)}", status_code=303)


@router.get("/logout")
def logout():
    """Logout endpoint."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("Authorization", path="/")
    response.delete_cookie("session", path="/") # Also clear authlib session
    return response
