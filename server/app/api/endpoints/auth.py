from fastapi import APIRouter, Depends, HTTPException, Request, Form, status, Response, Cookie
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from pathlib import Path

# Импорты из вашего проекта
from server.app.main import get_db
from server.app.dataBase.models.user import User
from server.app.api.deps import add_to_blacklist
from server.app.api.deps import get_current_user
from server.app.dataBase.models.session import Session as SessionModel

load_dotenv()

router = APIRouter(tags=["auth"])  

security = HTTPBearer()

# Настройка шаблонов
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Конфигурация аутентификации
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY не задан в .env!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str, db: Session) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
def get_user_from_token(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        return db.query(User).filter(User.username == username).first()
    except JWTError:
        return None

@router.post("/token")
async def login_for_access_token(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if username is None or password is None:
        try:
            data = await request.json()
            username = data.get("username")
            password = data.get("password")
        except:
            pass
    
    if not username or not password:
        raise HTTPException(status_code=400, detail="Требуются username и password") 
    
    user = authenticate_user(username, password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Неверные учетные данные", headers={"Content-Type": "application/json"})
    
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    redirect_url = "/api/admin/dashboard" if user.is_admin else "/api/user/dashboard"
    
    response = JSONResponse(content={
        "access_token": access_token,
        "token_type": "bearer",
        "redirect_url": "/api/admin/dashboard" if user.is_admin else "/api/user/dashboard"
    })
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60,
        secure=False,
        samesite="lax",
        path="/"
    )
    return response

@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(username, password, db)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный логин или пароль"}
        )
    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    redirect_url = "/api/admin/dashboard" if user.is_admin else "/api/user/dashboard"
    response = RedirectResponse(url=redirect_url, status_code=303)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax",
        path="/"
    )
    return response

# Добавляем новые роуты для разных типов пользователей
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse(url="/api/login", status_code=303)

    try:
        token = access_token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Проверяем, что пользователь админ
        if not payload.get("is_admin"):
            return RedirectResponse(url="/api/login", status_code=303)
        
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        
        return templates.TemplateResponse(
            "admin_dashboard.html",  # Ваш шаблон для админа
            {"request": request, "user": user}
        )
    except JWTError:
        return RedirectResponse(url="/api/login", status_code=303)

@router.get("/user/dashboard", response_class=HTMLResponse)
async def user_dashboard(
    request: Request,
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse(url="/api/login", status_code=303)

    try:
        token = access_token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return RedirectResponse(url="/api/login", status_code=303)
        
        sessions = db.query(SessionModel).filter(SessionModel.user_id == user.id).all()
        return templates.TemplateResponse(
            "dashboard.html",  # Обычный дашборд
            {"request": request, "user": user, "sessions": sessions}
        )
    except JWTError:
        return RedirectResponse(url="/api/login", status_code=303)

@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(username, password, db)
    if not user:
        # Вернуть страницу логина с ошибкой
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Неверный логин или пароль"}
        )

    access_token = create_access_token(
        data={"sub": user.username, "is_admin": user.is_admin},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response = RedirectResponse(
        url="/api/admin/dashboard" if user.is_admin else "/api/user/dashboard",
        status_code=303
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax",
        path="/"
    )
    return response


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, registration: str = None):
    context = {"request": request}
    if registration == "success":
        context["success"] = "Регистрация прошла успешно! Теперь вы можете войти."
    return templates.TemplateResponse("auth/login.html", context)

@router.post("/register", response_class=RedirectResponse)
async def register_user(
    full_name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином уже существует"
        )
    
    hashed_password = pwd_context.hash(password)
    new_user = User(
        full_name=full_name,
        username=username,
        password=hashed_password,
        registration_date=datetime.utcnow(),
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    
    return RedirectResponse(
        url="/api/login?registration=success",
        status_code=303
    )

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})
    
@router.get("/check-auth")
async def check_auth(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not access_token:
        raise HTTPException(status_code=401)
    
    try:
        token = access_token.replace("Bearer ", "")
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"status": "authenticated"}
    except JWTError:
        raise HTTPException(status_code=401)

@router.post("/logout")
def logout(response: Response,
    access_token: str = Cookie(None)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = access_token.replace("Bearer ", "")
    try:
        # Добавьте токен в blacklist, если нужно
        add_to_blacklist(token)
    except Exception as e:
        print("[LOGOUT ERROR]", e)

    response = JSONResponse({"message": "You have successfully logged out"})
    response.delete_cookie("access_token")
    return response