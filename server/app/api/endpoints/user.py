from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from server.app.api.deps import add_to_blacklist
from server.app.dataBase.base import settings
from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.user import User
from server.app.api.schemas import UserCreate, User as UserSchema, PasswordChange
from server.app.api.deps import get_current_user, get_admin_user, check_self_or_admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

router = APIRouter()

@router.post("/", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Создаем нового пользователя
    db_user = User(
        full_name=user.full_name,
        username=user.username,
        registration_date=datetime.now(), 
    )
    db_user.set_password(user.password)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserSchema], dependencies=[Depends(get_admin_user)])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
    ):
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserSchema)
def read_user(
    user_id: int, db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own data"
        )
        
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int,
    user_data: UserCreate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
        
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Проверяем, не занят ли username другим пользователем
    if user_data.username != db_user.username:
        existing_user = db.query(User).filter(
            User.username == user_data.username
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
    
    db_user.full_name = user_data.full_name
    db_user.username = user_data.username
    if user_data.password:
        db_user.set_password(user_data.password)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", dependencies=[Depends(get_admin_user)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

@router.post("/change-password", response_model=UserSchema)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверяем старый пароль
    if not current_user.verify_password(password_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Обновляем пароль
    current_user.set_password(password_data.new_password)
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.post("/logout")
def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    add_to_blacklist(token)
    return {"message": "You have successfully logged out"}