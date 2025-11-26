"""OAuth2 authentication for LeetCode Tracker."""

import logging
from typing import Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from authlib.integrations.starlette_client import OAuth

from .database import get_db
from . import models
from .config import settings

# Configure logging
logging.basicConfig(level=logging.getLevelName(settings.log_level))
logger = logging.getLogger(__name__)

# Инициализация OAuth
oauth = OAuth()

# Регистрация GitHub OAuth
oauth.register(
    name='github',
    client_id=settings.github_client_id,
    client_secret=settings.github_client_secret,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={'scope': 'user:email'},
    redirect_uri=settings.github_redirect_uri
)

# HTTP Bearer security
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создать JWT токен."""
    to_encode = data.copy()
    
    # Ensure 'sub' is a string (JWT standard requires it)
    if "sub" in to_encode and not isinstance(to_encode["sub"], str):
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.access_token_expire_hours)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def _get_token_from_request(request: Request) -> Optional[str]:
    """Extract token from header, cookie or query param."""
    # 1. Check Authorization header
    authorization = request.headers.get("Authorization")
    scheme, param = get_authorization_scheme_param(authorization)
    if scheme.lower() == "bearer":
        return param
    
    # 2. Check Cookie
    # Cookie might store just the token or "Bearer <token>"
    token = request.cookies.get("Authorization")
    if token:
        if token.startswith("Bearer "):
            return token[7:]
        return token
        
    # 3. Check Query Param (fallback)
    token = request.query_params.get("token")
    if token:
        return token
        
    return None

def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """
    Получить текущего пользователя из токена (опционально).
    Возвращает None если пользователь не авторизован.
    """
    token = _get_token_from_request(request)
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            logger.warning("Token payload missing 'sub'")
            return None
        # Convert string to int
        user_id = int(user_id_str)
    except JWTError as e:
        logger.debug(f"JWT Error in optional auth: {e}")
        return None
    except (ValueError, TypeError) as e:
        logger.warning(f"Invalid user_id in token: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in optional auth: {e}")
        return None
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    """
    Получить текущего пользователя из токена (обязательно).
    Raises HTTPException если пользователь не авторизован.
    """
    token = _get_token_from_request(request)
    if not token:
        logger.warning(f"Authentication failed: No token found. Cookies: {request.cookies.keys()}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            logger.warning("Authentication failed: Token missing 'sub'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Convert string to int
        user_id = int(user_id_str)
    except JWTError as e:
        logger.warning(f"Authentication failed: JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (ValueError, TypeError) as e:
        logger.warning(f"Authentication failed: Invalid user_id format: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        logger.warning(f"Authentication failed: User {user_id} not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_or_create_user(
    oauth_provider: str,
    oauth_id: str,
    email: Optional[str],
    username: str,
    avatar_url: Optional[str],
    db: Session
) -> models.User:
    """Получить существующего пользователя или создать нового."""
    
    # Попробовать найти пользователя по OAuth ID
    user = db.query(models.User).filter(
        models.User.oauth_provider == oauth_provider,
        models.User.oauth_id == oauth_id
    ).first()
    
    if user:
        # Обновить данные пользователя
        user.email = email
        user.avatar_url = avatar_url
        db.commit()
        db.refresh(user)
        return user
    
    # Создать нового пользователя
    # Проверить, занят ли username
    base_username = username
    counter = 1
    while db.query(models.User).filter(models.User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    user = models.User(
        username=username,
        email=email,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
        avatar_url=avatar_url
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
