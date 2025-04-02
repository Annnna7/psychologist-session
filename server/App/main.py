from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from server.App.DataBase.base import Base
from server.App.DataBase.models.user import User
from server.App.DataBase.models.session import Session
from server.App.DataBase.models.bracelet import Bracelet
from server.App.DataBase.models.notification import Notification
from server.App.DataBase.models.psychologist import Psychologist
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Подключение к базе данных
DATABASE_URL = "postgresql://postgres:123@localhost:5433/DataBase"
engine = create_engine(DATABASE_URL)
# Создаем сессию
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_connection_and_create_tables():
    try:
        # Создание всех таблиц, если их нет
        Base.metadata.create_all(bind=engine)
        print("Таблицы созданы или уже существуют")

        # Пробуем выполнить запрос
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))  # Используем text() для запроса
            print("Подключение к базе данных успешно!")

    except Exception as e:
        print(f"Ошибка подключения: {e}")

        
# Запуск
if __name__ == "__main__":
    check_connection_and_create_tables()
    #create_manager() 
