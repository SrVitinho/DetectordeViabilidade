from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base

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
    
    analyses = relationship("Analysis", back_populates="owner")
    
class Analysis(Base):
    __tablename__ = "Analysis"
    
    id = Column(Integer, primary_key=True, index=True)    
    owner_id = Column(Integer, ForeignKey("User.id"))
    owner = relationship("User", back_populates="analyses")
    
    request_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    
    data_criacao = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )