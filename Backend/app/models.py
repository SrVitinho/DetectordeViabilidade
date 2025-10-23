from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "User"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(128), index=True, unique=True, nullable=False)
    phone = Column(String(15), nullable=True)
    company = Column(String(128), nullable=True)
    password = Column(String(300), nullable=False)
    
    data_criacao = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )