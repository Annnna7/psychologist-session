from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from server.app.dataBase.sessions import get_db
from server.app.dataBase.models.session import Session as SessionModel
from server.app.dataBase.models.user import User 
from server.app.dataBase.models.psychologist import Psychologist
from server.app.api.schemas import SessionCreate, SessionSchema, SessionUpdate, SessionStatus
from server.app.api.deps import get_current_user_from_cookie  # Новый импорт

router = APIRouter(tags=["sessions"])

@router.post("/", response_model=SessionSchema, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: Request,
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Создание новой терапевтической сессии
    - Требуется аутентификация через куки
    - Статус по умолчанию: 'pending'
    """
    try:
        # Проверка существования психолога
        psychologist = db.query(Psychologist).get(session_data.psychologist_id)
        if not psychologist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Психолог не найден"
            )

        db_session = SessionModel(
            user_id=current_user.id,
            psychologist_id=session_data.psychologist_id,
            date_time=session_data.date_time,
            duration=session_data.duration,
            price=session_data.price,
            status=session_data.status.value,
            notes=session_data.notes
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при создании сессии"
        )

@router.get("/", response_model=List[SessionSchema])
async def read_sessions(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status: Optional[SessionStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Получение списка сессий текущего пользователя
    - Фильтрация по статусу (опционально)
    - Пагинация через skip/limit
    """
    query = db.query(SessionModel).filter(SessionModel.user_id == current_user.id)
    
    if status:
        query = query.filter(SessionModel.status == status.value)
        
    return query.order_by(SessionModel.date_time)\
               .offset(skip)\
               .limit(limit)\
               .all()

@router.get("/{session_id}", response_model=SessionSchema)
async def read_session(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Получение детальной информации о сессии
    - Доступ только для владельца или администратора
    """
    session = db.query(SessionModel).get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сессия не найдена"
        )
    
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этой сессии"
        )
        
    return session

@router.put("/{session_id}", response_model=SessionSchema)
async def update_session(
    request: Request,
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Обновление информации о сессии
    - Доступ только для владельца или администратора
    - Частичное обновление разрешено
    """
    session = db.query(SessionModel).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет прав для обновления")

    try:
        update_data = session_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'status' and value:
                setattr(session, field, value.value)
            else:
                setattr(session, field, value)
                
        db.commit()
        db.refresh(session)
        return session
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обновления: {str(e)}"
        )

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    request: Request,
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    """
    Удаление сессии
    - Доступ только для владельца или администратора
    """
    session = db.query(SessionModel).get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Нет прав для удаления")

    try:
        db.delete(session)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка удаления: {str(e)}"
        )