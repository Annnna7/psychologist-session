from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from sqlalchemy import text
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к БД
DATABASE_URL = "postgresql://postgres:123@localhost:5433/DataBase"
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Подключение к БД успешно")
    except Exception as e:
        logger.error(f"× Ошибка подключения: {e}")
        raise

def create_tables():
    from server.app.dataBase.base import Base
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Таблицы созданы/проверены")
    except Exception as e:
        logger.error(f"× Ошибка создания таблиц: {e}")
        raise

app = FastAPI(
    title="Psychologist Session API",
    version="1.0.0"
)

# Инициализация при старте
@app.on_event("startup")
def startup():
    logger.info("Запуск инициализации...")
    check_connection()
    create_tables()
    logger.info("Инициализация завершена")

# Подключение роутеров (синхронные версии)
from server.app.api.endpoints import user, auth, psychologist, session, notification, bracelet  # и другие

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
    uvicorn.run(app, host="0.0.0.0", port=8000)