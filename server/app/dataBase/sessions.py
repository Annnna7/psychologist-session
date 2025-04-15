from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .base import Base

# Синхронный URL подключения
DATABASE_URL = "postgresql://postgres:123@localhost:5433/DataBase"

# Создаем синхронный engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    echo=True  # Логирование SQL-запросов
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def get_db():
    """
    Генератор синхронной сессии для зависимостей.
    Использование:
    db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()