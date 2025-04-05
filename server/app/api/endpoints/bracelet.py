from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.bracelet import Bracelet as BraceletModel
from server.app.api.schemas import BraceletCreate, Bracelet as BraceletSchema

router = APIRouter()

@router.post(
    "/",
    response_model=BraceletSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new bracelet"
)
async def create_bracelet(
    bracelet: BraceletCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bracelet with:
    - **settings**: JSON string with bracelet configuration
    - **user_id**: ID of associated user (must be unique)
    """
    try:
        db_bracelet = BraceletModel(**bracelet.dict())
        db.add(db_bracelet)
        await db.commit()
        await db.refresh(db_bracelet)
        return db_bracelet
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating bracelet: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[BraceletSchema],
    summary="Get list of bracelets"
)
async def read_bracelets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve bracelets with pagination:
    - **skip**: Number of items to skip
    - **limit**: Maximum items to return
    """
    result = await db.execute(
        select(BraceletModel)
        .order_by(BraceletModel.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get(
    "/{bracelet_id}",
    response_model=BraceletSchema,
    summary="Get bracelet by ID"
)
async def read_bracelet(
    bracelet_id: int, 
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed bracelet information by ID
    """
    bracelet = await db.get(BraceletModel, bracelet_id)
    if not bracelet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bracelet not found"
        )
    return bracelet

@router.put(
    "/{bracelet_id}",
    response_model=BraceletSchema,
    summary="Update bracelet information"
)
async def update_bracelet(
    bracelet_id: int,
    bracelet_data: BraceletCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update bracelet configuration by ID
    """
    db_bracelet = await db.get(BraceletModel, bracelet_id)
    if not db_bracelet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bracelet not found"
        )

    try:
        for key, value in bracelet_data.dict().items():
            setattr(db_bracelet, key, value)
        
        await db.commit()
        await db.refresh(db_bracelet)
        return db_bracelet
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating bracelet: {str(e)}"
        )

@router.delete(
    "/{bracelet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bracelet"
)
async def delete_bracelet(
    bracelet_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete bracelet by ID
    """
    bracelet = await db.get(BraceletModel, bracelet_id)
    if not bracelet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bracelet not found"
        )

    try:
        await db.delete(bracelet)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting bracelet: {str(e)}"
        )