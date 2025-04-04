from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.session import Session as SessionModel
from server.app.api.schemas import SessionCreate, Session as SessionSchema

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post(
    "/",
    response_model=SessionSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new session"
)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new therapy session with the following details:
    - **user_id**: ID of the user
    - **psychologist_id**: ID of the psychologist
    - **date_time**: Date and time of the session
    - **duration**: Duration in minutes
    - **price**: Session price
    - **status**: Current status (planned/completed/cancelled)
    """
    try:
        db_session = SessionModel(**session_data.dict())
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        return db_session
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating session: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[SessionSchema],
    summary="Get list of sessions"
)
async def read_sessions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a list of therapy sessions with pagination:
    - **skip**: Number of items to skip
    - **limit**: Maximum number of items to return
    """
    result = await db.execute(
        select(SessionModel)
        .order_by(SessionModel.date_time)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get(
    "/{session_id}",
    response_model=SessionSchema,
    summary="Get session by ID"
)
async def read_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific session by its ID
    """
    session = await db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@router.put(
    "/{session_id}",
    response_model=SessionSchema,
    summary="Update session information"
)
async def update_session(
    session_id: int,
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update session information by ID
    """
    db_session = await db.get(SessionModel, session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    try:
        for key, value in session_data.dict().items():
            setattr(db_session, key, value)
        
        await db.commit()
        await db.refresh(db_session)
        return db_session
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating session: {str(e)}"
        )

@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session"
)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a session by ID
    """
    session = await db.get(SessionModel, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    try:
        await db.delete(session)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting session: {str(e)}"
        )