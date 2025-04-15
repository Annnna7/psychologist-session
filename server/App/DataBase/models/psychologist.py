from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext
from zoneinfo import ZoneInfo
from ..base import Base

# Модель Психолог (Psychologist)
class Psychologist(Base):
    __tablename__ = 'psychologists'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    rating = Column(Float, nullable=False)

    # Связи
    users = relationship('User', secondary='user_psychologist', back_populates='psychologists')
    sessions = relationship('Session', back_populates='psychologist')

    def repr(self):
        return f"<Psychologist(id={self.id}, full_name={self.full_name})>"


# Таблица для связи многие-ко-многим между User и Psychologist
user_psychologist = Table(
    'user_psychologist', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('psychologist_id', Integer, ForeignKey('psychologists.id'))
)