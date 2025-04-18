from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from typing import Optional, List, Callable, Awaitable
from starlette.middleware.base import BaseHTTPMiddleware
import re

from server.app.api.deps import SECRET_KEY, ALGORITHM, is_token_revoked

class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exempt_routes: Optional[List[str]] = None):
        super().__init__(app)
        self.exempt_routes = exempt_routes or [
            "/",           
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/docs",
            "/api/openapi.json",
            "/api/token",
            "/api/users/",
            "/api/health"
        ]

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Пропускаем exempt routes
        if any(re.fullmatch(pattern, path) for pattern in self.exempt_routes):
            return await call_next(request)
        
        # Проверяем авторизацию
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )
        
        token = auth_header.split(" ")[1]

        if is_token_revoked(token):  # Новая проверка
            return JSONResponse(
                status_code=401,
                content={"detail": "Token revoked"}
            )
    
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid token"}
            )
        
        return await call_next(request)