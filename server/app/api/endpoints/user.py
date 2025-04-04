from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exc
from typing import List
from datetime import datetime

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.user import User as UserModel
from server.app.api.schemas import UserCreate, User as UserSchema

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user"
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user with the following information:
    - **full_name**: User's full name
    - **username**: Unique username
    - **password**: User's password (will be hashed)
    """
    try:
        # Проверяем, существует ли пользователь с таким username
        existing_user = await db.execute(
            select(UserModel).where(UserModel.username == user_data.username)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )

        db_user = UserModel(
            full_name=user_data.full_name,
            username=user_data.username,
            registration_date=datetime.now()
        )
        db_user.set_password(user_data.password)
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except exc.SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/",     response_model=List[UserSchema])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of users with pagination:
    - **skip**: Number of items to skip
    - **limit**: Maximum number of items to return
    """
    try:
        result = await db.execute(
            select(UserModel)
            .order_by(UserModel.registration_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    except exc.SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Get user by ID"
)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific user by ID
    """
    user = await db.get(UserModel, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put(
    "/{user_id}",
    response_model=UserSchema,
    summary="Update user information"
)
async def update_user(
    user_id: int,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user information by ID
    """
    try:
        db_user = await db.get(UserModel, user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user_data.username != db_user.username:
            existing_user = await db.execute(
                select(UserModel).where(UserModel.username == user_data.username)
            )
            if existing_user.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        db_user.full_name = user_data.full_name
        db_user.username = user_data.username
        if user_data.password:
            db_user.set_password(user_data.password)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except exc.SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user"
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user by ID
    """
    try:
        user = await db.get(UserModel, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await db.delete(user)
        await db.commit()
    except exc.SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )