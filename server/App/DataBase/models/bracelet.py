from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext
from zoneinfo import ZoneInfo
from ..base import Base

# Модель Браслет (Bracelet)
class Bracelet(Base):
    __tablename__ = 'bracelets'
    id = Column(Integer, primary_key=True)
    settings = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    # Связи
    user = relationship('User', back_populates='bracelet')
    notifications = relationship('Notification', back_populates='bracelet')

    def __repr__(self):
        return f"<Bracelet(id={self.id}, settings={self.settings})>"