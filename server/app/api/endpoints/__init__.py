# Импортируем все роутеры из отдельных модулей
from .auth import router as auth_router
from .user import router as users_router
from .psychologist import router as psychologists_router
from .session import router as sessions_router
from .notification import router as notifications_router
from .bracelet import router as bracelets_router

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
print(f"Python path: {sys.path}")  # Проверьте пути

# Явно указываем, что должно быть доступно при импорте из этого пакета
__all__ = [
    'auth_router',
    'user_router',
    'psychologist_router',
    'session_router',
    'notification_router',
    'bracelet_router'
]