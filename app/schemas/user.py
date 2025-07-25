from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    alias: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    send_daily_agenda: Optional[bool] = False
    agenda_send_time: Optional[constr(regex=r"^([01]\d|2[0-3]):[0-5]\d$")] = None
    timezone: Optional[str] = None
    provider: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True
    provider: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    alias: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    send_daily_agenda: Optional[bool] = None
    agenda_send_time: Optional[constr(regex=r"^([01]\d|2[0-3]):[0-5]\d$")] = None
    timezone: Optional[str] = None
    provider: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    token_expiry: Optional[datetime] = None

class UserCreateByAdmin(UserBase):
    password: str
    role: str 
    provider: Optional[str] = None
    refresh_token: Optional[str] = None
    access_token: Optional[str] = None
    token_expiry: Optional[datetime] = None 