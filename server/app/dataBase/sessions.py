# server/app/db/session.py (асинхронная версия)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .base import Base
from sqlalchemy import create_engine

DATABASE_URL = "postgresql+asyncpg://postgres:123@localhost:5433/DataBase"
SYNC_DATABASE_URL = "postgresql://postgres:123@localhost:5433/DataBase"

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Асинхронный движок и сессия
async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Синхронный движок (для миграций)
sync_engine = create_engine(SYNC_DATABASE_URL)

async def get_db():
    """Генератор асинхронной сессии для зависимостей"""
    async with AsyncSessionLocal() as session:
        yield session