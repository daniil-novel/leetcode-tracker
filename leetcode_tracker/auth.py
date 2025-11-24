"""OAuth2 authentication for LeetCode Tracker."""

import os
import logging
from typing import Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from authlib.integrations.starlette_client import OAuth
from passlib.context import CryptContext

from .database import get_db
from . import models, schemas

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Секретный ключ для JWT (в продакшене использовать переменную окружения)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24 * 7  # 7 дней

# OAuth конфигурация
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Инициализация OAuth
oauth = OAuth()

# Регистрация GitHub OAuth (redirect_uri будет динамический)
oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    refresh_token_url=None,
    client_kwargs={'scope': 'user:email'},
)

# Регистрация Google OAuth (redirect_uri будет динамический)
oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# HTTP Bearer security
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создать JWT токен."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    """
    Получить текущего пользователя из токена (опционально).
    Возвращает None если пользователь не авторизован.
    """
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Получить текущего пользователя из токена (обязательно).
    Raises HTTPException если пользователь не авторизован.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
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
    display_name: Optional[str],
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
        
        # Обновить display_name если он есть
        if display_name:
            profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user.id).first()
            if profile:
                profile.display_name = display_name
                
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
    
    # Создать профиль
    profile = models.UserProfile(
        user_id=user.id,
        display_name=display_name or username
    )
    db.add(profile)
    
    # Создать настройки приватности
    privacy = models.PrivacySettings(user_id=user.id)
    db.add(privacy)
    
    db.commit()
    
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хешировать пароль."""
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str, db: Session) -> Optional[models.User]:
    """Аутентифицировать пользователя по username и паролю."""
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        return None
    if not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_user(username: str, password: str, email: Optional[str], db: Session) -> models.User:
    """Создать нового пользователя."""
    # Проверить, что username уникален
    existing = db.query(models.User).filter(models.User.username == username).first()
    if existing:
        raise ValueError("Username already exists")
    
    # Создать пользователя
    user = models.User(
        username=username,
        password_hash=get_password_hash(password),
        email=email
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Создать профиль
    profile = models.UserProfile(user_id=user.id)
    db.add(profile)
    
    # Создать настройки приватности
    privacy = models.PrivacySettings(user_id=user.id)
    db.add(privacy)
    
    db.commit()
    
    return user
