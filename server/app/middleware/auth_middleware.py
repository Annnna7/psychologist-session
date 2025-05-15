from fastapi import Request
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
            "/static/.*"  # Для статических файлов
        ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Пропускаем exempt routes
        if any(re.fullmatch(pattern, path) for pattern in self.exempt_routes):
            return await call_next(request)
        
        # Проверяем авторизацию 
        token = None
        
        # 1. Проверяем куки
        if "access_token" in request.cookies:
            token = request.cookies["access_token"].replace("Bearer ", "")
        
        # 2. Проверяем Authorization header
        elif request.headers.get("Authorization"):
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )
        
        if is_token_revoked(token):
            return JSONResponse(
                status_code=401,
                content={"detail": "Token revoked"}
            )
    
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY.get_secret_value(),
                algorithms=[settings.ALGORITHM]
            )
            request.state.user = payload.get("sub")
        except JWTError as e:
            return JSONResponse(
                status_code=401,
                content={"detail": f"Invalid token: {str(e)}"}
            )
        
        return await call_next(request)