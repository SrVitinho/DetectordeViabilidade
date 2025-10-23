from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    company: str
    phone: str
    password: str
    
class UserUpdate(BaseModel):
    id: int
    name: str 
    company: str
    phone: str
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    company: str
    data_criacao: datetime

    class Config:
       from_attributes = True
    
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class UserDataLogin(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    class Config:
        from_attributes = True

class ResponseDataLogin(BaseModel):
    token: str
    usuario: UserDataLogin

class UserResponseLogin(BaseModel):
    status: str
    message: str
    data: ResponseDataLogin
    
class UserResponseRegister(BaseModel):
    status: str
    message: str
    data: UserResponse