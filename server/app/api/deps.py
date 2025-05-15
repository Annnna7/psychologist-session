from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Annotated, Dict, Optional
from datetime import datetime, timedelta
from pydantic import ValidationError

# Импортируем настройки из base.py
from server.app.dataBase.base import settings
from server.app.dataBase.models.user import User
from server.app.dataBase.sessions import get_db
from server.app.api.schemas import TokenData

# Используем настройки из settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Черный список токенов 
token_blacklist: Dict[str, datetime] = {}

def is_token_revoked(token: str) -> bool:
    """Проверяет, отозван ли токен"""
    return token in token_blacklist

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Проверка на отозванный токен
        if is_token_revoked(token):
            raise credentials_exception
        
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # Валидация через Pydantic
        token_data = TokenData(username=username)
    except (JWTError, ValidationError) as exc:
        print(f"[AUTH ERROR] Token validation failed: {exc}")
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        print(f"[AUTH ERROR] User {token_data.username} not found")
        raise credentials_exception
    
    # Проверка активного статуса пользователя
    if not user.is_active:
        print(f"[AUTH WARNING] Inactive user {user.username} tried to access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user

def add_to_blacklist(token: str, expires_delta: Optional[timedelta] = None) -> bool:
    """Добавляет токен в черный список с обработкой ошибок"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        
        if exp:
            token_blacklist[token] = datetime.fromtimestamp(exp)
        elif expires_delta:
            token_blacklist[token] = datetime.utcnow() + expires_delta
        else:
            token_blacklist[token] = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        return True
    except JWTError as exc:
        print(f"[BLACKLIST ERROR] Failed to add token: {exc}")
        return False

def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Проверка прав администратора"""
    if not current_user.is_admin:
        print(f"[AUTH WARNING] User {current_user.username} attempted admin access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def check_self_or_admin(
    user_id: int,
    current_user: User = Depends(get_current_user)
) -> User:
    """Проверка доступа к ресурсу (владелец или администратор)"""
    if not current_user.is_admin and current_user.id != user_id:
        print(f"[AUTH WARNING] User {current_user.username} attempted unauthorized access to user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own account"
        )
    return current_user