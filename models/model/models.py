from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from passlib.context import CryptContext
from zoneinfo import ZoneInfo

Base = declarative_base()

# Настроим хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Модель Пользователь (User)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    registration_date = Column(DateTime, nullable=False)

    # Связи
    bracelet = relationship('Bracelet', back_populates='user', uselist=False)
    psychologists = relationship('Psychologist', secondary='user_psychologist', back_populates='users')
    sessions = relationship('Session', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, full_name={self.full_name})>"
    
    # Метод для хэширования пароля
    def set_password(self, password):
        self.password = pwd_context.hash(password)

    # Метод для проверки пароля
    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

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

# Модель Психолог (Psychologist)
class Psychologist(Base):
    __tablename__ = 'psychologists'
    id = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    rating = Column(Float, nullable=False)

    # Связи
    users = relationship('User', secondary='user_psychologist', back_populates='psychologists')
    sessions = relationship('Session', back_populates='psychologist')

    def __repr__(self):
        return f"<Psychologist(id={self.id}, full_name={self.full_name})>"

# Таблица для связи многие-ко-многим между User и Psychologist
user_psychologist = Table(
    'user_psychologist', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('psychologist_id', Integer, ForeignKey('psychologists.id'))
)

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