from __future__ import annotations

from pathlib import Path
import logging

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .database import Base, engine
from . import models
from .config import settings
from .routers import auth, tasks, stats

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create DB tables on startup (simple dev approach)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_title, debug=settings.debug)

# Note: Proxy headers are handled by uvicorn with --proxy-headers flag
# This is configured in the systemd service file

# Add TrustedHostMiddleware to prevent Host header attacks
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=[
        "novel-cloudtech.com", 
        "*.novel-cloudtech.com", 
        "localhost", 
        "127.0.0.1",
        "v353999.hosted-by-vdsina.com"
    ]
)

# Add session middleware for OAuth
# With ProxyHeadersMiddleware, request.url.scheme should now correctly be 'https'
app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.secret_key,
    https_only=True,  # Ensure session cookie is only sent over HTTPS
    max_age=settings.access_token_expire_hours * 3600,  # Same as JWT expiry
)

logger.info(f"🚀 Starting {settings.app_title}")
logger.info(f"📊 Log level: {settings.log_level}")
logger.info(f"🔒 HTTPS-only cookies: enabled")
logger.info(f"� Proxy headers: handled by uvicorn --proxy-headers flag")

# Exception handler for 401 Unauthorized - Redirect to login
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Clear any existing auth cookies / session data if present on redirect
        response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("Authorization", path="/")
        response.delete_cookie("session", path="/")
        return response
    # For other HTTP exceptions, re-raise to use FastAPI's default handling
    raise exc


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIST_DIR = BASE_DIR.parent / "frontend" / "dist"

# Mount static files from React build
if FRONTEND_DIST_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")),
        name="assets",
    )

# Serve React App for root and fallback - MUST be defined BEFORE including routers
# so that API routes take precedence
@app.get("/")
async def serve_root():
    """Serve React app root."""
    return FileResponse(FRONTEND_DIST_DIR / "index.html")

# Include routers - these will take precedence over the catch-all below
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(stats.router)

# Catch-all route for SPA routing - this should be LAST
# Exclude API paths to prevent conflicts
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    # Don't serve SPA for API paths
    if full_path.startswith(("api/", "auth/", "add/", "stats/")):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Check if file exists in dist (e.g. favicon.ico, robots.txt)
    file_path = FRONTEND_DIST_DIR / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
        
    # Otherwise serve index.html for SPA routing
    return FileResponse(FRONTEND_DIST_DIR / "index.html")
