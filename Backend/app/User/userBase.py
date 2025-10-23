from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    company: str
    phone: str
    password: str
    
class UserUpdate(BaseModel):
    ID: int
    name: str 
    company: str
    phone: str
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    company: str
    phone: str
    data_criacao: datetime

    class Config:
        orm_mode = True