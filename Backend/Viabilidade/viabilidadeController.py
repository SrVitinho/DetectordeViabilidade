from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
import json
import requests

from database import SessionLocal
from models import Viabilidade, User
from  Viabilidade.viabilidadeBase import ViabilidadeRequest, ViabilidadeResponse, DetalhesResultado, ResultadoViabilidade, DadosViabilidadeResponse
from ML.loader import predict_viabilidade
from auth import get_current_user, get_db

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

router = APIRouter(
    prefix='/api/viabilidade',
    tags=['Viabilidade']
)

@router.post("/analisar", response_model=ViabilidadeResponse)
async def analisar_viabilidade(
    dados: ViabilidadeRequest, 
    user: user_dependency, 
    db: db_dependency
):
    try:
        if "-" in dados.localizacao.cep:
            dados.localizacao.cep = int(dados.localizacao.cep.replace("-",""))

        else:
            dados.localizacao.cep = int(dados.localizacao.cep)
        
        r = requests.get(f"https://viacep.com.br/ws/{dados.localizacao.cep}/json/")

        cdMunic = r.json()["ibge"]
        print(cdMunic)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "100",
                "message": "Deu nois",
                "code": 200
            }
        )
    
    except Exception as err:
            print(err)
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "CEP inválido ou não informado.",
                "code": 400
            }
        )
    
    if not dados.empresa.cnae or len(dados.empresa.cnae) < 4:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "CNAE inválido ou não informado.",
                "code": 400
            }
        )
    
    valor_mei = 1 if dados.empresa.isMei else 0
    
    input_modelo = [
        dados.localizacao.cep,
        dados.empresa.cnae,
        dados.empresa.capitalInicial,
        valor_mei
    ]#ver se ordem importa
    
    try:
        score_calculado = predict_viabilidade(input_modelo)
        sera_viavel = score_calculado >= 60.0       #analisar como definir isso
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            score_calculado = 0.0,
            sera_viavel = False,
            content={
                "status": "error",
                "message": f"Erro ao processar a análise de viabilidade: {e}",
                "code": 500
            }
            
        )
        
        
    #verificar como retornar isso aq
    detalhes_mock = {
        "analise_localizacao": f"O bairro {dados.localizacao.bairro} possui alto fluxo para o CNAE {dados.empresa.cnae}.",
        "analise_mercado": "Baixa saturação de concorrentes na região.",
        "analise_economica": f"Capital de R$ {dados.empresa.capitalInicial} é adequado para o início.",
        "fatores_risco": ["Variação cambial", "Reformas na rua prevista"],
        "recomendacoes": ["Investir em marketing local", "Contratar 2 funcionários"]
    }
    
    nova_analise = Viabilidade(
        user_id=user.id,
        cep=dados.localizacao.cep,
        cnae=dados.empresa.cnae,
        capital_inicial=dados.empresa.capitalInicial,
        is_mei=dados.empresa.isMei,
        pontuacao=float(score_calculado),
        viavel=sera_viavel,
        analise_localizacao=detalhes_mock["analise_localizacao"],
        analise_mercado=detalhes_mock["analise_mercado"],
        analise_economica=detalhes_mock["analise_economica"],
        fatores_risco=json.dumps(detalhes_mock["fatores_risco"]),
        recomendacoes=json.dumps(detalhes_mock["recomendacoes"])
    )

    db.add(nova_analise)
    db.commit()
    db.refresh(nova_analise)
    
    return ViabilidadeResponse(
        status="success",
        message="Análise de viabilidade realizada com sucesso",
        data=DadosViabilidadeResponse(
            viabilidade_id=nova_analise.id,
            resultado=ResultadoViabilidade(
                viavel=nova_analise.viavel,
                pontuacao=nova_analise.pontuacao,
                detalhes=DetalhesResultado(
                    analise_localizacao=nova_analise.analise_localizacao,
                    analise_mercado=nova_analise.analise_mercado,
                    analise_economica=nova_analise.analise_economica,
                    fatores_risco=json.loads(nova_analise.fatores_risco),
                    recomendacoes=json.loads(nova_analise.recomendacoes)
                )
            ),
            data_analise=nova_analise.data_analise
        ),
        code=200
    )
