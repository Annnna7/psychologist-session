from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str   

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class User(UserBase):
    id: int
    registration_date: datetime

    class Config:
        from_attributes = True

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class PsychologistBase(BaseModel):
    full_name: str
    specialty: str
    rating: float

class PsychologistCreate(PsychologistBase):
    pass

class Psychologist(PsychologistBase):
    id: int

    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    user_id: int
    psychologist_id: int
    date_time: datetime
    duration: int
    price: float
    status: str

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: int

    class Config:
        from_attributes = True

class BraceletBase(BaseModel):
    settings: str
    user_id: int

class BraceletCreate(BraceletBase):
    pass

class Bracelet(BraceletBase):
    id: int

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    bracelet_id: int
    session_id: int
    message_type: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None