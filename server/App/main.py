from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from server.app.dataBase.base import Base
from server.app.dataBase.models.user import User
from server.app.dataBase.models.session import Session
from server.app.dataBase.models.bracelet import Bracelet
from server.app.dataBase.models.notification import Notification
from server.app.dataBase.models.psychologist import Psychologist
from datetime import datetime
from sqlalchemy.exc import IntegrityError


# Импортируем роутеры
from server.app.api.endpoints import (
    auth, 
    user, 
    psychologist, 
    session, 
    notification, 
    bracelet
)

# Подключение к базе данных
DATABASE_URL = "postgresql+asyncpg://postgres:1508@localhost:5433/DataBase"
SYNC_DATABASE_URL = "postgresql://postgres:1508@localhost:5433/DataBase"

# Создаем асинхронный engine для FastAPI
engine = create_async_engine(DATABASE_URL)
# Создаем синхронный engine для проверки подключения
sync_engine = create_engine(SYNC_DATABASE_URL)

# Создаем сессии
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=sync_engine
)
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False
)

# Создаем FastAPI приложение
app = FastAPI(title="Psychologist Session API")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(psychologist.router)
app.include_router(session.router)
app.include_router(notification.router)
app.include_router(bracelet.router)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def check_connection_and_create_tables():
    try:
        # Создание всех таблиц, если их нет
        Base.metadata.create_all(bind=sync_engine)
        print("Таблицы созданы или уже существуют")

        # Пробуем выполнить запрос
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))  # Используем text() для запроса
            print("Подключение к базе данных успешно!")

    except Exception as e:
        print(f"Ошибка подключения: {e}")

from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    check_connection_and_create_tables()
    yield

app = FastAPI(title="Psychologist Session API", lifespan=lifespan)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Psychologist Session API",
        "docs": "http://127.0.0.1:8000/docs",
        "redoc": "http://127.0.0.1:8000/redoc"
    }

        
# Запуск
if __name__ == "main":
    import uvicorn
    check_connection_and_create_tables()
    uvicorn.run(app, host="0.0.0.0", port=8000)