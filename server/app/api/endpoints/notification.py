from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.notification import Notification
from server.app.api.schemas import NotificationCreate, Notification
from sqlalchemy import select  # Для синхронной версии
from typing import List

router = APIRouter()

@router.post("/", response_model=Notification)
async def create_notification(
    notification: NotificationCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_notification = Notification(**notification.dict())
    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification

@router.get("/", response_model=List[Notification])
async def read_notifications(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Notification).offset(skip).limit(limit))
    notifications = result.scalars().all()
    return notifications

@router.get("/{notification_id}", response_model=Notification)
async def read_notification(
    notification_id: int, 
    db: AsyncSession = Depends(get_db)
):
    notification = await db.get(Notification, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/{notification_id}", response_model=Notification)
async def update_notification(
    notification_id: int, 
    notification: NotificationCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_notification = await db.get(Notification, notification_id)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    for key, value in notification.dict().items():
        setattr(db_notification, key, value)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int, 
    db: AsyncSession = Depends(get_db)
):
    notification = await db.get(Notification, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    await db.delete(notification)
    await db.commit()
    return {"message": "Notification deleted successfully"}