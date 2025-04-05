from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from datetime import datetime

# Импорты должны быть согласованы:
from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.user import User  # SQLAlchemy модель
from server.app.api.schemas import UserCreate, User as UserSchema  # Pydantic схемы

router = APIRouter()

@router.post("/", response_model=UserSchema)  # Используем Pydantic схему
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(
        full_name=user.full_name,
        username=user.username,
        registration_date=datetime.now()
    )
    db_user.set_password(user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/", response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserSchema)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    user_id: int,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    db_user = await db.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.full_name = user_data.full_name
    db_user.username = user_data.username
    if user_data.password:
        db_user.set_password(user_data.password)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}