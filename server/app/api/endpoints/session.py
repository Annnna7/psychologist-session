from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.session import Session
from server.app.api.schemas import SessionCreate, Session
from sqlalchemy import select  # Для синхронной версии
from typing import List

router = APIRouter()

@router.post("/", response_model=Session)
async def create_session(
    session: SessionCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_session = Session(**session.dict())
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    return db_session

@router.get("/", response_model=List[Session])
async def read_sessions(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Session).offset(skip).limit(limit))
    sessions = result.scalars().all()
    return sessions

@router.get("/{session_id}", response_model=Session)
async def read_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/{session_id}", response_model=Session)
async def update_session(
    session_id: int, 
    session: SessionCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_session = await db.get(Session, session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    for key, value in session.dict().items():
        setattr(db_session, key, value)
    await db.commit()
    await db.refresh(db_session)
    return db_session

@router.delete("/{session_id}")
async def delete_session(
    session_id: int, 
    db: AsyncSession = Depends(get_db)
):
    session = await db.get(Session, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    return {"message": "Session deleted successfully"}