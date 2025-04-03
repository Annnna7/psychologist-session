from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.user import User
from server.app.api.schemas import UserCreate, User
from datetime import datetime
from sqlalchemy import select  # Для синхронной версии
from typing import List

router = APIRouter()

@router.post("/", response_model=User)
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

@router.get("/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.full_name = user.full_name
    db_user.username = user.username
    db_user.set_password(user.password)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.delete("/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}