from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from sqlalchemy import text
import logging
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from server.app.dataBase.base import settings
from fastapi.middleware.cors import CORSMiddleware 

from server.app.middleware.auth_middleware import AuthMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

app.add_middleware(AuthMiddleware)

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
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

print("Текущие настройки:")
print(f"Algorithm: {settings.ALGORITHM}")
print(f"Token expires in: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")

# Настройка путей
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

