from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.session import Session as SessionModel
from server.app.api.schemas import SessionCreate, Session as SessionSchema

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionSchema)
def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new therapy session
    """
    try:
        db_session = SessionModel(
            user_id=session_data.user_id,
            psychologist_id=session_data.psychologist_id,
            date_time=session_data.date_time,
            duration=session_data.duration,
            price=session_data.price,
            status=session_data.status
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating session: {str(e)}"
        )

@router.get("/", response_model=List[SessionSchema])
def read_sessions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of therapy sessions with pagination
    - **skip**: Number of items to skip
    - **limit**: Maximum number of items to return
    """
    return db.query(SessionModel)\
            .order_by(SessionModel.date_time)\
            .offset(skip)\
            .limit(limit)\
            .all()

@router.get("/{session_id}", response_model=SessionSchema)
def read_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific session by its ID
    """
    session = db.query(SessionModel).get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return session

@router.put("/{session_id}", response_model=SessionSchema)
def update_session(
    session_id: int,
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """
    Update session information by ID
    """
    db_session = db.query(SessionModel).get(session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    try:
        for key, value in session_data.dict().items():
            setattr(db_session, key, value)
        
        db.commit()
        db.refresh(db_session)
        return db_session
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating session: {str(e)}"
        )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a session by ID
    """
    session = db.query(SessionModel).get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    try:
        db.delete(session)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting session: {str(e)}"
        )