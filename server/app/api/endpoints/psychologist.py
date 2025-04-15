from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from server.app.dataBase.sessions import get_db
from server.app.api.schemas import PsychologistCreate, Psychologist
from sqlalchemy import select
from typing import List

from server.app.dataBase.models.psychologist import Psychologist as PsychologistModel
from server.app.api.schemas import Psychologist as PsychologistSchema

router = APIRouter()

@router.post("/", response_model=PsychologistSchema)
def create_psychologist(
    psychologist: PsychologistCreate,
    db: Session = Depends(get_db)
):
    db_psychologist = PsychologistModel(**psychologist.dict())
    db.add(db_psychologist)
    db.commit()
    db.refresh(db_psychologist)
    return db_psychologist

@router.get("/", response_model=List[PsychologistSchema])
def read_psychologists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    psychologists = db.query(PsychologistModel).offset(skip).limit(limit).all()
    return psychologists

@router.get("/{psychologist_id}", response_model=Psychologist)
def read_psychologist(
    psychologist_id: int, 
    db: Session = Depends(get_db)
):
    psychologist = db.get(PsychologistModel, psychologist_id)
    if psychologist is None:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    return psychologist

@router.put("/{psychologist_id}", response_model=PsychologistSchema)
def update_psychologist(
    psychologist_id: int, 
    psychologist_data: PsychologistCreate, 
    db: Session = Depends(get_db)
):
    db_psychologist = db.get(PsychologistModel, psychologist_id)
    if db_psychologist is None:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    # Обновляем поля
    for key, value in psychologist_data.dict().items():
        setattr(db_psychologist, key, value)
    
    db.commit()
    db.refresh(db_psychologist)
    return db_psychologist

@router.delete("/{psychologist_id}")
def delete_psychologist(
    psychologist_id: int, 
    db: Session = Depends(get_db)
):
    psychologist = db.get(PsychologistModel, psychologist_id)
    if psychologist is None:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    db.delete(psychologist)
    db.commit()
    return {"message": "Psychologist deleted successfully"}