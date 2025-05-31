from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from typing import Optional, List
from starlette.middleware.base import BaseHTTPMiddleware
import re

from server.app.dataBase.base import settings
from server.app.api.deps import is_token_revoked

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_routes: Optional[List[str]] = None):
        super().__init__(app)
        self.exempt_routes = exempt_routes or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/token",
            "/api/register",
            "/login",
            "/register",
            r"/static/.*",  # Регулярка для статических файлов
            r"/favicon\.ico"
        ]
        self.compiled_patterns = [re.compile(pattern) for pattern in self.exempt_routes]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Пропускаем exempt routes
        if any(pattern.fullmatch(path) for pattern in self.compiled_patterns):
            return await call_next(request)
        
        token = self.extract_token(request)
        
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if is_token_revoked(token):
            raise HTTPException(
                status_code=401,
                detail="Token revoked"
            )
    
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY.get_secret_value(),
                algorithms=[settings.ALGORITHM]
            )
            request.state.user_id = payload.get("user_id")  # Более полезно чем sub
            request.state.is_admin = payload.get("is_admin", False)
        except JWTError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token: {str(e)}"
            )
        
        return await call_next(request)

    def extract_token(self, request: Request) -> Optional[str]:
        """Извлекает токен из кук или заголовка"""
        # 1. Проверяем куки
        if "access_token" in request.cookies:
            cookie = request.cookies["access_token"]
            if cookie.startswith("Bearer "):
                return cookie[7:]  # Удаляем "Bearer "
            return cookie
        
        # 2. Проверяем Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        
        return None