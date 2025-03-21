import sys
import os
from sqlalchemy import create_engine  # Импортируем create_engine
from sqlalchemy.orm import sessionmaker

# Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.model.models import Base  # Импортируем Base для создания всех таблиц

# Подключение к базе данных через Docker
DATABASE_URL = "postgresql://postgres:123@localhost:5433/postgres"

# Создаем подключение к базе данных
engine = create_engine(DATABASE_URL)

# Сессия для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание всех таблиц
Base.metadata.create_all(bind=engine)