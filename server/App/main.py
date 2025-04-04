from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from contextlib import asynccontextmanager
import asyncio

# Перенесем импорт роутеров после создания app, чтобы избежать циклических импортов

# Подключение к базе данных
DATABASE_URL = "postgresql+asyncpg://postgres:123@localhost:5433/DataBase"
SYNC_DATABASE_URL = "postgresql://postgres:123@localhost:5433/DataBase"

# Создаем асинхронный engine с настройками
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    echo=True
)

# Синхронный engine только для миграций
sync_engine = create_engine(SYNC_DATABASE_URL)

# Асинхронная сессия
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    """Генератор асинхронной сессии для зависимостей"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def check_async_connection():
    """Проверка асинхронного подключения"""
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            print("✓ Асинхронное подключение к БД успешно")
        except Exception as e:
            print(f"× Ошибка асинхронного подключения: {e}")

def check_sync_connection():
    """Проверка синхронного подключения (для миграций)"""
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Синхронное подключение к БД успешно")
    except Exception as e:
        print(f"× Ошибка синхронного подключения: {e}")

def create_tables():
    """Создание таблиц (синхронно, для Alembic)"""
    from server.app.dataBase.base import Base  # Локальный импорт для избежания циклических зависимостей
    try:
        Base.metadata.create_all(bind=sync_engine)
        print("✓ Таблицы созданы/проверены")
    except Exception as e:
        print(f"× Ошибка создания таблиц: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст жизненного цикла приложения"""
    print("\n" + "="*50)
    print("Запуск инициализации приложения...")
    
    # Проверка подключений
    check_sync_connection()
    await check_async_connection()
    create_tables()
    
    print("Инициализация завершена успешно!")
    print("="*50 + "\n")
    
    yield
    
    # При завершении работы
    await engine.dispose()
    sync_engine.dispose()
    print("✓ Подключения к БД корректно закрыты")

app = FastAPI(
    title="Psychologist Session API",
    description="API для системы психологических сессий",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Теперь импортируем роутеры после создания app
from server.app.api.endpoints import (
    auth, 
    user, 
    psychologist, 
    session, 
    notification, 
    bracelet
)

# Подключаем роутеры
app.include_router(auth.router, prefix="/api", tags=["Аутентификация"])
app.include_router(user.router, prefix="/api/users", tags=["Пользователи"])
app.include_router(psychologist.router, prefix="/api/psychologists", tags=["Психологи"])
app.include_router(session.router, prefix="/api/sessions", tags=["Сессии"])
app.include_router(notification.router, prefix="/api/notifications", tags=["Уведомления"])
app.include_router(bracelet.router, prefix="/api/bracelets", tags=["Браслеты"])

@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Добро пожаловать в Psychologist Session API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1
    )