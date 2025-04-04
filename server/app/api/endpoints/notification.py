from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.notification import Notification as NotificationModel  # SQLAlchemy модель
from server.app.api.schemas import NotificationCreate, Notification as NotificationSchema  # Pydantic схемы

router = APIRouter()

@router.post("/", response_model=NotificationSchema)
async def create_notification(
    notification: NotificationCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Создаем экземпляр SQLAlchemy модели
    db_notification = NotificationModel(**notification.dict())
    
    db.add(db_notification)
    await db.commit()
    await db.refresh(db_notification)
    return db_notification  # Будет автоматически преобразовано в NotificationSchema

@router.get("/", response_model=List[NotificationSchema])
async def read_notifications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(NotificationModel).offset(skip).limit(limit))
    notifications = result.scalars().all()
    return notifications

@router.get("/{notification_id}", response_model=NotificationSchema)
async def read_notification(
    notification_id: int, 
    db: AsyncSession = Depends(get_db)
):
    notification = await db.get(NotificationModel, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/{notification_id}", response_model=NotificationSchema)
async def update_notification(
    notification_id: int, 
    notification_data: NotificationCreate, 
    db: AsyncSession = Depends(get_db)
):
    db_notification = await db.get(NotificationModel, notification_id)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    # Обновляем поля
    for key, value in notification_data.dict().items():
        setattr(db_notification, key, value)
    
    await db.commit()
    await db.refresh(db_notification)
    return db_notification

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int, 
    db: AsyncSession = Depends(get_db)
):
    notification = await db.get(NotificationModel, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await db.delete(notification)
    await db.commit()
    return {"message": "Notification deleted successfully"}