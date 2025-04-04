import sys
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

# Импортируем модели напрямую
from server.app.dataBase.base import Base
from server.app.dataBase.models.user import User
from server.app.dataBase.models.bracelet import Bracelet
from server.app.dataBase.models.psychologist import Psychologist
from server.app.dataBase.models.session import Session
from server.app.dataBase.models.notification import Notification

# Настройка подключения к БД
DATABASE_URL = "postgresql://postgres:123@localhost:5433/DataBase"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Настроим хеширование паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Создание таблиц (если их нет)
Base.metadata.create_all(bind=engine)

# Функция для создания тестовых пользователей
def create_users():
    """Создание тестовых пользователей."""
    users = [
        User(
            full_name="Иван Иванов",
            username="ivanov",
            password="password123",  # Пароль будет хэширован
            registration_date=datetime.now()
        ),
        User(
            full_name="Мария Петрова",
            username="petrova",
            password="qwerty456",
            registration_date=datetime.now()
        ),
    ]

    for user in users:
        user.set_password(user.password)  # Хэшируем пароль
        session.add(user)

    session.commit()
    print("Пользователи добавлены")

# Функция для создания тестовых браслетов
def create_bracelets():
    """Создание тестовых браслетов."""
    users = session.query(User).all()
    if users:
        bracelets = [
            Bracelet(settings="theme=light;vibration=on", user=users[0]),
            Bracelet(settings="theme=dark;vibration=off", user=users[1]),
        ]
        session.add_all(bracelets)
        session.commit()
        print("Браслеты добавлены")
    else:
        print("Не хватает пользователей для создания браслетов")

# Функция для создания тестовых психологов
def create_psychologists():
    """Создание тестовых психологов."""
    psychologists = [
        Psychologist(
            full_name="Алексей Смирнов",
            specialty="Когнитивно-поведенческая терапия",
            rating=4.8
        ),
        Psychologist(
            full_name="Елена Кузнецова",
            specialty="Семейная психология",
            rating=4.9
        ),
    ]
    session.add_all(psychologists)
    session.commit()
    print("Психологи добавлены")

# Функция для создания тестовых сеансов
def create_sessions():
    """Создание тестовых сеансов."""
    users = session.query(User).all()
    psychologists = session.query(Psychologist).all()
    if users and psychologists:
        sessions = [
            Session(
                user=users[0],
                psychologist=psychologists[0],
                date_time=datetime.now() + timedelta(days=1),
                duration=60,
                price=2000.0,
                status="Запланирован"
            ),
            Session(
                user=users[1],
                psychologist=psychologists[1],
                date_time=datetime.now() + timedelta(days=2),
                duration=90,
                price=3000.0,
                status="Запланирован"
            ),
        ]
        session.add_all(sessions)
        session.commit()
        print("Сеансы добавлены")
    else:
        print("Не хватает данных для создания сеансов")

# Функция для создания тестовых уведомлений
def create_notifications():
    """Создание тестовых уведомлений."""
    bracelets = session.query(Bracelet).all()
    sessions = session.query(Session).all()
    users = session.query(User).all()
    if bracelets and sessions and users:
        notifications = [
            Notification(
                bracelet=bracelets[0],
                session=sessions[0],
                user=users[0]
            ),
            Notification(
                bracelet=bracelets[1],
                session=sessions[1],
                user=users[1]
            ),
        ]
        session.add_all(notifications)
        session.commit()
        print("Уведомления добавлены")
    else:
        print("Не хватает данных для создания уведомлений")

if __name__ == "__main__":
    create_users()
    create_bracelets()
    create_psychologists()
    create_sessions()
    session.close()