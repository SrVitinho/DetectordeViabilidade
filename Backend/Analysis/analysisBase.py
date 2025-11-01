from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class AnalysisLocationBase(BaseModel):
    endereco: str = Field(..., pattern=r"^\d{5}-\d{3}$")
    rua: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    uf: str = Field(..., min_length=2, max_length=2)
    
class AnalysisCompanyBase(BaseModel):
    cnae: str
    capitalInicial: float = Field(..., gt=0.0)
    isMei: bool
    qualificacaoDoResponsavel: str
    
class AnalysisBase(BaseModel):
    location: AnalysisLocationBase
    company: AnalysisCompanyBase

class AnalysisDetailsResponse(BaseModel):
    analise_localizacao: str
    analise_mercado: str
    analise_economica: str
    fatores_risco: List[str]
    recomendacoes: List[str]

class ViabilityAnalysisResponse(BaseModel):
    viavel: bool
    pontuacao: float = Field(..., ge=0.0, le=100.0)
    detalhes: AnalysisDetailsResponse
    
class ViabilityReport(BaseModel):
    viabilidade_id: int
    resultado: ViabilityAnalysisResponse
    data_analise: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
class ViabilityResponse(BaseModel):
    status: str = "success"
    message: str
    data: ViabilityReport