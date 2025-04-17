from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Annotated, Dict
from datetime import datetime, timedelta

from server.app.dataBase.models.user import User
from server.app.dataBase.sessions import get_db
from server.app.api.schemas import TokenData

import os

# Конфигурация JWT
SECRET_KEY = os.getenv("SECRET_KEY") or "fallback-secret-key"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Черный список токенов (для реализации logout)
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
    
    # Проверка на отозванный токен
    if is_token_revoked(token):
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def add_to_blacklist(token: str, expires_delta: timedelta = None):
    """Добавляет токен в черный список"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")
        if exp:
            token_blacklist[token] = datetime.fromtimestamp(exp)
        elif expires_delta:
            token_blacklist[token] = datetime.utcnow() + expires_delta
        else:
            token_blacklist[token] = datetime.utcnow() + timedelta(minutes=15)
    except JWTError:
        pass