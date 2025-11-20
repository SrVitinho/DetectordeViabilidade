from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text
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
    
    analises = relationship("Viabilidade", back_populates="usuario")
    
class Viabilidade(Base):
    __tablename__ = "Viabilidade"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("User.id"))
    
    cep = Column(String(20))
    rua = Column(String(150))
    numero = Column(String(20))
    complemento = Column(String(100), nullable=True)
    bairro = Column(String(100))
    cidade = Column(String(100))
    uf = Column(String(2))
    
    cnae = Column(String(20))
    capital_incial = Column(Float)
    is_mei = Column(Boolean)
    
    pontuacao = Column(Float)
    viavel = Column(Boolean)
    
    analise_localizacao = Column(Text)
    analise_mercado = Column(Text)
    analise_economica = Column(Text)
    
    fatores_risco = Column(Text)
    recomendacoes = Column(Text)
    
    data_analise = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    usuario = relationship("User", back_populates="analises")
    