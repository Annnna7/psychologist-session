from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta, datetime
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from pydantic import SecretStr
# Импортируем из database.py
from server.app.main import get_db
from server.app.dataBase.models.user import User
from server.app.api.schemas import Token

load_dotenv()

router = APIRouter()

SECRET_KEY = SecretStr(os.getenv("SECRET_KEY"))
if not SECRET_KEY.get_secret_value():
    raise RuntimeError("SECRET_KEY не задан в .env!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

def authenticate_user(username: str, password: str, db: Session):
    try:
        print(f"Searching for user: {username}")
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print("User not found")
            return False
            
        print(f"Found user: {user.username}")
        if not pwd_context.verify(password, user.password):
            print("Password verification failed")
            return False
            
        print("Password verified successfully")
        return user
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta: 
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    print(f"\nAttempting login for user: {form_data.username}")
    
    user = authenticate_user(form_data.username, form_data.password, db)
    
    if not user:
        print("Authentication failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    print("Authentication successful! Token generated")
    return {"access_token": access_token, "token_type": "bearer"}