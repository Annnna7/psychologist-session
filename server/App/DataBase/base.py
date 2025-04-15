from sqlalchemy.ext.declarative import declarative_base
from pydantic_settings import BaseSettings
from datetime import timedelta

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Настройки JWT
class Settings(BaseSettings):
    SECRET_KEY: str = "your-very-secret-key"  # Замените на реальный ключ (минимум 32 символа)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Для автоматического обновления токенов
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        case_sensitive = True

# Инициализация настроек
settings = Settings()

# Дополнительные утилиты для удобства
def get_token_expires():
    return timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)