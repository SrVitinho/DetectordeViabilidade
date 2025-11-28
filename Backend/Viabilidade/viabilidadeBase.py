from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LocalizacaoBase(BaseModel):
    cep: str
    
class EmpresaBase(BaseModel):
    cnae: str
    naturezaJuridica: int
    qualificacaoDoResponsavel: int
    capitalInicial: float
    isMei: bool = False
    
class ViabilidadeRequest(BaseModel):
    localizacao: LocalizacaoBase
    empresa: EmpresaBase
    
class DetalhesResultado(BaseModel):
    analise_localizacao: int

class ResultadoViabilidade(BaseModel):
    pontuacao: float
    detalhes: DetalhesResultado
    
class LocalizacaoResponse(BaseModel):
    cep: str
    rua: Optional[str] = None
    bairro: Optional[str] = None
    cidade: str
    uf: str
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    
class DadosViabilidadeResponse(BaseModel):
    viabilidade_id: int
    resultado: ResultadoViabilidade
    localizacao: LocalizacaoResponse
    empresa: EmpresaBase
    data_analise: datetime
    
class ViabilidadeResponse(BaseModel):
    status: str
    message: str
    data: Optional[DadosViabilidadeResponse] = None
    code: Optional[int] = None
    
class HistoricoItem(BaseModel):
    id: int
    cnae: str
    local: str
    cep: str
    pontuacao: float
    viavel: bool
    data_analise: datetime

    class Config:
        from_attributes = True

class HistoricoResponse(BaseModel):
    status: str
    message: str
    data: List[HistoricoItem]
    code: int