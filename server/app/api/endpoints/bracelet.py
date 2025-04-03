from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.bracelet import Bracelet
from server.app.api.schemas import BraceletCreate, Bracelet
from sqlalchemy import select  # Для синхронной версии
from typing import List

router = APIRouter()

@router.post("/", response_model=Bracelet)
async def create_bracelet(
    bracelet: BraceletCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_bracelet = Bracelet(**bracelet.dict())
    db.add(db_bracelet)
    await db.commit()
    await db.refresh(db_bracelet)
    return db_bracelet

@router.get("/", response_model=List[Bracelet])
async def read_bracelets(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Bracelet).offset(skip).limit(limit))
    bracelets = result.scalars().all()
    return bracelets

@router.get("/{bracelet_id}", response_model=Bracelet)
async def read_bracelet(
    bracelet_id: int, 
    db: AsyncSession = Depends(get_db)
):
    bracelet = await db.get(Bracelet, bracelet_id)
    if bracelet is None:
        raise HTTPException(status_code=404, detail="Bracelet not found")
    return bracelet

@router.put("/{bracelet_id}", response_model=Bracelet)
async def update_bracelet(
    bracelet_id: int, 
    bracelet: BraceletCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_bracelet = await db.get(Bracelet, bracelet_id)
    if db_bracelet is None:
        raise HTTPException(status_code=404, detail="Bracelet not found")
    for key, value in bracelet.dict().items():
        setattr(db_bracelet, key, value)
    await db.commit()
    await db.refresh(db_bracelet)
    return db_bracelet

@router.delete("/{bracelet_id}")
async def delete_bracelet(
    bracelet_id: int, 
    db: AsyncSession = Depends(get_db)
):
    bracelet = await db.get(Bracelet, bracelet_id)
    if bracelet is None:
        raise HTTPException(status_code=404, detail="Bracelet not found")
    await db.delete(bracelet)
    await db.commit()
    return {"message": "Bracelet deleted successfully"}