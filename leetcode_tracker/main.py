from __future__ import annotations

from pathlib import Path
import logging

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.proxy_headers import ProxyHeadersMiddleware

from .database import Base, engine
from . import models
from .config import settings
from .routers import auth, tasks, stats, frontend

# Configure logging
logging.basicConfig(
    level=logging.getLevelName(settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create DB tables on startup (simple dev approach)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_title, debug=settings.debug)

# Add ProxyHeadersMiddleware to trust Nginx headers
# This is CRITICAL for proper HTTPS handling behind reverse proxy
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts=["*"])

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
logger.info(f"🔄 Proxy headers: trusted")

# Exception handler for 401 Unauthorized - Redirect to login
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        # Clear any existing auth cookies / session data if present on redirect
        response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
        response.delete_cookie("Authorization", path="/")
        response.delete_cookie("session", path="/")
        return response
    # For other HTTP exceptions, use default handler
    return await request.app.default_exception_handler(request, exc)


BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)
# Templates are handled by dependencies.py now

# Include routers
app.include_router(frontend.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(stats.router)

# All other content (endpoints) removed as they are now in routers
