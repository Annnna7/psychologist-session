from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.psychologist import Psychologist as PsychologistModel  # SQLAlchemy модель
from server.app.api.schemas import PsychologistCreate, Psychologist as PsychologistSchema  # Pydantic схемы

router = APIRouter()

@router.post("/", response_model=PsychologistSchema)
async def create_psychologist(
    psychologist: PsychologistCreate,
    db: AsyncSession = Depends(get_db)
):
    # Создаем экземпляр SQLAlchemy модели
    db_psychologist = PsychologistModel(**psychologist.dict())
    
    db.add(db_psychologist)
    await db.commit()
    await db.refresh(db_psychologist)
    return db_psychologist

@router.get("/", response_model=List[PsychologistSchema])
async def read_psychologists(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(PsychologistModel).offset(skip).limit(limit))
    psychologists = result.scalars().all()
    return psychologists

@router.get("/{psychologist_id}", response_model=PsychologistSchema)
async def read_psychologist(
    psychologist_id: int, 
    db: AsyncSession = Depends(get_db)
):
    psychologist = await db.get(PsychologistModel, psychologist_id)
    if psychologist is None:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    return psychologist

@router.put("/{psychologist_id}", response_model=PsychologistSchema)
async def update_psychologist(
    psychologist_id: int, 
    psychologist_data: PsychologistCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_psychologist = await db.get(PsychologistModel, psychologist_id)
    if db_psychologist is None:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    # Обновляем поля
    for key, value in psychologist_data.dict().items():
        setattr(db_psychologist, key, value)
    
    await db.commit()
    await db.refresh(db_psychologist)
    return db_psychologist

@router.delete("/{psychologist_id}")
async def delete_psychologist(
    psychologist_id: int, 
    db: AsyncSession = Depends(get_db)
):
    psychologist = await db.get(PsychologistModel, psychologist_id)
    if psychologist is None:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    await db.delete(psychologist)
    await db.commit()
    return {"message": "Psychologist deleted successfully"}