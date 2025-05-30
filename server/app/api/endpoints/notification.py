from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.notification import Notification as NotificationModel
from server.app.api.schemas import NotificationCreate, Notification as NotificationSchema

router = APIRouter()

@router.post("/", response_model=NotificationSchema)
def create_notification(
    notification: NotificationCreate, 
    db: Session = Depends(get_db)
):  
    # Создаем уведомление
    db_notification = NotificationModel(
        bracelet_id=notification.bracelet_id,
        session_id=notification.session_id,
        message_type=notification.message_type
    )
    
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.get("/", response_model=List[NotificationSchema])
def read_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    notifications = db.query(NotificationModel).offset(skip).limit(limit).all()
    return notifications

@router.get("/{notification_id}", response_model=NotificationSchema)
def read_notification(
    notification_id: int, 
    db: Session = Depends(get_db)
):
    notification = db.get(NotificationModel, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/{notification_id}", response_model=NotificationSchema)
def update_notification(
    notification_id: int, 
    notification_data: NotificationCreate, 
    db: Session = Depends(get_db)
):
    db_notification = db.get(NotificationModel, notification_id)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    for key, value in notification_data.dict().items():
        setattr(db_notification, key, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification

@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int, 
    db: Session = Depends(get_db)
):
    notification = db.get(NotificationModel, notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted successfully"}

@router.get("/user/{user_id}", response_model=List[NotificationSchema])
def get_user_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    notifications = db.query(NotificationModel).filter(NotificationModel.bracelet_id == user_id).all()
    return notifications
