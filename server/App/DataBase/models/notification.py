from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext
from zoneinfo import ZoneInfo
from ..base import Base

# Модель Уведомления (Notification)
class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    bracelet_id = Column(Integer, ForeignKey('bracelets.id'))
    session_id = Column(Integer, ForeignKey('sessions.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    # Связи
    bracelet = relationship('Bracelet', back_populates='notifications')
    session = relationship('Session', back_populates='notifications')
    user = relationship('User')

    def __repr__(self):
        return f"<Notification(id={self.id})>"