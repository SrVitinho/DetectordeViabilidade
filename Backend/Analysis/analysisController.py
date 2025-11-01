from random import random
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlalchemy.orm import Session

from models import Analysis, User
from auth import db_dependency, auth_dependency

from .analysisBase import (
    AnalysisBase, 
    ViabilityResponse, 
    ViabilityAnalysisResponse,
    AnalysisDetailsResponse,
    ViabilityReport
)

router = APIRouter(
    prefix='/viabilidade',
    tags=['Analysis']
)

def simulacao(data: AnalysisBase) -> ViabilityAnalysisResponse:
    empresa = data.company
    viavel = empresa.capitalInicial >= 5000 and not empresa.isMei
    pontuacao = random.uniform(70, 93) if viavel else random.uniform(20, 50)
    
    detalhes = AnalysisDetailsResponse(
        analise_localizacao= "Bom fluxo de pessoas",
        analise_mercado= "Mercado em crescimento",
        analise_economica= "Capital inicial de R${empresa.capitalInicial} é adequado",
        fatores_risco= ["Concorrência alta", "Baixa margem de lucro"],
        recomendacoes= ["Marketing digital", "Diversificação de produtos"]
    )
    
    return ViabilityAnalysisResponse(
        viabilidade= viavel,
        pontuacao= pontuacao,
        detalhes= detalhes
    )

@router.post("/analisar", response_model=ViabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_viability_analysis(
    analysis_data: AnalysisBase, 
    db: db_dependency,
    current_user: auth_dependency
):
    resultado_analise = simulacao(analysis_data)
    
    db_analysis = Analysis(
        owner_id= current_user.id,
        request_data= analysis_data.model_dump(),
        result_data= resultado_analise.model_dump()
    )

    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    report_data = ViabilityReport(
        viabilidade_id= db_analysis.id,
        resultado= resultado_analise,
        data_analise= db_analysis.data_criacao
    )
    
    return ViabilityResponse(
        status="success",
        message="Análise de viabilidade criada com sucesso",
        data= report_data
    )

