from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from model.models import Base, User
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Подключение к базе данных
DATABASE_URL = "postgresql://postgres:123@localhost:5433/postgres"
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

# Функция для создания пользователя
def create_user():
    with SessionLocal() as session:
        username = "user123"
        existing_user = session.query(User).filter(User.username == username).first()
        
        if existing_user:
            print(f"Пользователь с username {existing_user.username} уже существует.")
            return

        try:
            new_user = User(
                full_name="Иван Иванов",
                username=username,
                password="password123",
                registration_date=datetime.now()
            )
            new_user.set_password(new_user.password)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            print(f"Пользователь {new_user.full_name} добавлен с ID {new_user.id}")

        except IntegrityError:
            session.rollback()
            print(f"Ошибка: Пользователь с username {username} уже существует.")
        
# Запуск
if __name__ == "__main__":
    check_connection_and_create_tables()
    #create_manager() 
