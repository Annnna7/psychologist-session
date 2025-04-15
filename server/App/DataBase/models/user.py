from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext
from zoneinfo import ZoneInfo
from ..base import Base

# Настроим хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модель Пользователь (User)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    registration_date = Column(DateTime, nullable=False)

    # Связи
    bracelet = relationship('Bracelet', back_populates='user', uselist=False)
    psychologists = relationship('Psychologist', secondary='user_psychologist', back_populates='users')
    sessions = relationship('Session', back_populates='user')

    # Добавляем property для совместимости
    @property
    def hashed_password(self):
        return self.password
    
    def set_password(self, password):
        self.password = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)