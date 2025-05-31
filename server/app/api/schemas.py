from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str   

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    #is_admin: bool = False
    
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

class SessionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class SessionBase(BaseModel):
    psychologist_id: int = Field(..., description="ID психолога")
    date_time: datetime = Field(..., description="Дата и время сеанса")
    duration: int = Field(..., gt=0, description="Длительность в минутах")
    price: float = Field(..., gt=0, description="Стоимость сеанса")
    notes: Optional[str] = Field(None, max_length=1000, description="Дополнительные заметки")

    @validator('date_time')
    def validate_future_date(cls, v):
        if v < datetime.now():
            raise ValueError("Дата сеанса должна быть в будущем")
        return v

class SessionCreate(SessionBase):
    status: Optional[SessionStatus] = Field(SessionStatus.PENDING, description="Статус сеанса")

class SessionUpdate(BaseModel):
    date_time: Optional[datetime] = None
    duration: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    status: Optional[SessionStatus] = None
    notes: Optional[str] = None

class SessionSchema(SessionBase):
    id: int
    user_id: int
    psychologist_id: int
    status: SessionStatus
    #created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

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