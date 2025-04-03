# server/app/db/session.py (синхронная версия)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base

DATABASE_URL = "postgresql://postgres:123@localhost:5433/DataBase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()