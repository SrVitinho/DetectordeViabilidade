from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float, Text, BigInteger, Numeric
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
    
    cep = Column(Integer)
    cidade = Column(Integer)
    uf = Column(String(2))
    
    cnae = Column(String(20))
    is_mei = Column(Boolean)
    
    pontuacao = Column(Float)
    
    data_analise = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    usuario = relationship("User", back_populates="analises")
    
class DadosMunic(Base):
    __tablename__ = "DadosMunic"

    column1 = Column(Integer, primary_key=True, index=True)
    Nome_Mun = Column(String(128), nullable=False, index=True)
    ID_MUN = Column(Integer, unique=True, nullable=False, index=True)
    UF = Column(String(2), nullable=False, index=True)

    PIB_2016 = Column(BigInteger, nullable=True)
    PIB_2017 = Column(BigInteger, nullable=True)
    PIB_2018 = Column(BigInteger, nullable=True)
    PIB_2019 = Column(BigInteger, nullable=True)
    PIB_2020 = Column(BigInteger, nullable=True)
    PIB_2021 = Column(BigInteger, nullable=True)

    Quant_Benificiarios = Column(Integer, nullable=True)
    Inss_Pagou_2022 = Column(BigInteger, nullable=True)
    INSS_Ticket_Medio = Column(Numeric(20, 2), nullable=True)
    PIB_Medio = Column(Numeric(20, 2), nullable=True)
    PIB_Delta_Abs = Column(Numeric(20, 2), nullable=True)
    PIB_Cresc = Column(Numeric(20, 2), nullable=True)

    População_Masc_2021 = Column(Integer, nullable=True)
    População_Fem_2021 = Column(Integer, nullable=True)

    De_0_a_4_anos = Column(Integer, nullable=True)
    De_5_a_9_anos = Column(Integer, nullable=True)
    De_10_a_14_anos = Column(Integer, nullable=True)
    De_15_a_19_anos = Column(Integer, nullable=True)
    De_20_a_24_anos = Column(Integer, nullable=True)
    De_25_a_29_anos = Column(Integer, nullable=True)
    De_30_a_34_anos = Column(Integer, nullable=True)
    De_35_a_39_anos = Column(Integer, nullable=True)
    De_40_a_44_anos = Column(Integer, nullable=True)
    De_45_a_49_anos = Column(Integer, nullable=True)
    De_50_a_54_anos = Column(Integer, nullable=True)
    De_55_a_59_anos = Column(Integer, nullable=True)
    De_60_a_64_anos = Column(Integer, nullable=True)
    De_65_a_69_anos = Column(Integer, nullable=True)
    De_70_a_74_anos = Column(Integer, nullable=True)
    De_75_a_79_anos = Column(Integer, nullable=True)
    De_80_anos_ou_mais = Column(Integer, nullable=True)

    Pib_2016_Corrigido = Column(Numeric(20, 2), nullable=True)
    PIB_Delta_Corr = Column(Numeric(20, 2), nullable=True)
    PIB_Cresc_Corr = Column(Numeric(20, 2), nullable=True)
    POP_22 = Column(Integer, nullable=True)

class MicroEmpresasFechadasPorAno(Base):
    __tablename__ = "MICROEMPRESASFECHADASSPORANO"

    EmpresasSimilaresFechadas = Column(Integer, nullable=False)
    ANOBAIXA = Column(Integer, nullable=False, primary_key=True, index=True)
    CNAE_FISCAL_PRINCIPAL = Column('CNAE FISCAL PRINCIPAL', String, primary_key=True)
    CEP = Column(String(8), nullable=False, primary_key=True, index=True)

class MicroEmpresasAbertasPorAno(Base):
    __tablename__ = "MICROEMPRESASABERTASPORANO"

    EmpresasSimilaresAbertas = Column(Integer, nullable=False)
    ANOABERTURA = Column(Integer, nullable=False, primary_key=True, index=True)
    CNAE_FISCAL_PRINCIPAL = Column('CNAE FISCAL PRINCIPAL', String, primary_key=True)
    CEP = Column(String(8), nullable=False, primary_key=True, index=True)
