from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext
from zoneinfo import ZoneInfo
from ..base import Base

# Модель Сеанс (Session)
class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    psychologist_id = Column(Integer, ForeignKey('psychologists.id'))
    date_time = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)

    # Связи
    user = relationship('User', back_populates='sessions')
    psychologist = relationship('Psychologist', back_populates='sessions')
    notifications = relationship('Notification', back_populates='session')

    def __repr__(self):
        return f"<Session(id={self.id}, status={self.status})>"