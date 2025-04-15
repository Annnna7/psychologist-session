from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def create_bracelet(
    bracelet: BraceletCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new bracelet with:
    - **settings**: JSON string with bracelet configuration
    - **user_id**: ID of associated user (must be unique)
    """
    try:
        db_bracelet = BraceletModel(**bracelet.dict())
        db.add(db_bracelet)
        db.commit()
        db.refresh(db_bracelet)
        return db_bracelet
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating bracelet: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[BraceletSchema],
    summary="Get list of bracelets"
)
def read_bracelets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve bracelets with pagination:
    - **skip**: Number of items to skip
    - **limit**: Maximum items to return
    """
    bracelets = db.query(BraceletModel)\
                 .order_by(BraceletModel.id)\
                 .offset(skip)\
                 .limit(limit)\
                 .all()
    return bracelets

@router.get(
    "/{bracelet_id}",
    response_model=BraceletSchema,
    summary="Get bracelet by ID"
)
def read_bracelet(
    bracelet_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get detailed bracelet information by ID
    """
    bracelet = db.get(BraceletModel, bracelet_id)
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
def update_bracelet(
    bracelet_id: int,
    bracelet_data: BraceletCreate,
    db: Session = Depends(get_db)
):
    """
    Update bracelet configuration by ID
    """
    db_bracelet = db.get(BraceletModel, bracelet_id)
    if not db_bracelet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bracelet not found"
        )

    try:
        for key, value in bracelet_data.dict().items():
            setattr(db_bracelet, key, value)
        
        db.commit()
        db.refresh(db_bracelet)
        return db_bracelet
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating bracelet: {str(e)}"
        )

@router.delete(
    "/{bracelet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bracelet"
)
def delete_bracelet(
    bracelet_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete bracelet by ID
    """
    bracelet = db.get(BraceletModel, bracelet_id)
    if not bracelet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bracelet not found"
        )

    try:
        db.delete(bracelet)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting bracelet: {str(e)}"
        )