from sqlalchemy.ext.declarative import declarative_base
from pydantic_settings import BaseSettings
from datetime import timedelta
from pydantic import SecretStr
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv() 

# Базовый класс для моделей SQLAlchemy
Base = declarative_base()

# Настройки JWT
class Settings(BaseSettings):
    SECRET_KEY: SecretStr  
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "forbid"  # Запретит неизвестные переменные


settings = Settings()

def get_token_expires():
    return timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)