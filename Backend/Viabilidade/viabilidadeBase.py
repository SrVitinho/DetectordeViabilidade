from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LocalizacaoBase(BaseModel):
    cep: str
    
class EmpresaBase(BaseModel):
    cnae: str
    naturezaJuridica: int
    qualificacaoDoResponsavel: int
    isMei: bool = False
    
class ViabilidadeRequest(BaseModel):
    localizacao: LocalizacaoBase
    empresa: EmpresaBase
    
class DetalhesResultado(BaseModel):
    analise_localizacao: int

class ResultadoViabilidade(BaseModel):
    pontuacao: float
    detalhes: DetalhesResultado
    
class DadosViabilidadeResponse(BaseModel):
    viabilidade_id: int
    resultado: ResultadoViabilidade
    data_analise: datetime
    
class ViabilidadeResponse(BaseModel):
    status: str
    message: str
    data: Optional[DadosViabilidadeResponse] = None
    code: Optional[int] = None