from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    full_name: str
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    registration_date: datetime

    class Config:
        from_attributes = True

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
    user_id: int

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