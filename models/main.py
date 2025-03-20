from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base

# Подключение к базе данных
DATABASE_URL = "postgresql+pg8000://postgres:123@localhost:5432/DataBase"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def check_connection_and_create_tables():
    try:
        # Создание всех таблиц, если их нет
        Base.metadata.create_all(bind=engine)
        print("Таблицы созданы или уже существуют")

        # Пробуем выполнить запрос
        with Session() as session:
            session.execute(text("SELECT 1"))  # Используем text() для запроса
            print("Подключение к базе данных успешно!")

    except Exception as e:
        print(f"Ошибка подключения: {e}")
        
# Запуск
if __name__ == "__main__":
    check_connection_and_create_tables()
    #create_manager() 
