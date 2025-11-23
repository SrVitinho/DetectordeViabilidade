from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
import json
import requests
import pandas as pd

from database import SessionLocal
from models import Viabilidade, User, DadosMunic, MicroEmpresasAbertasPorAno, MicroEmpresasFechadasPorAno
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
            dados.localizacao.cep = (dados.localizacao.cep.replace("-",""))

        else:
            dados.localizacao.cep = (dados.localizacao.cep)
        print(dados.localizacao.cep)
        r = requests.get(f"https://viacep.com.br/ws/{dados.localizacao.cep}/json/")

        cdMunic = r.json()["ibge"]
        print(cdMunic)
    
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
    
    if "/" in dados.empresa.cnae:
            dados.empresa.cnae = dados.empresa.cnae.replace("/","")

    if "-" in dados.empresa.cnae:
            dados.empresa.cnae = int(dados.empresa.cnae.replace("-",""))

    dados.empresa.cnae = int(dados.empresa.cnae)
    
    valor_mei = 'S' if dados.empresa.isMei else 'N'
    
    municObservado = db.query(DadosMunic).filter(DadosMunic.ID_MUN == cdMunic).first()

    cnaesAbertos = db.query(MicroEmpresasAbertasPorAno).filter((MicroEmpresasAbertasPorAno.ANOABERTURA == 2024) , (MicroEmpresasAbertasPorAno.CEP == dados.localizacao.cep) , (MicroEmpresasAbertasPorAno.CNAE_FISCAL_PRINCIPAL == dados.empresa.cnae)).first()

    cnaesFechados = db.query(MicroEmpresasFechadasPorAno).filter((MicroEmpresasFechadasPorAno.ANOBAIXA == 2024) , (MicroEmpresasFechadasPorAno.CEP == dados.localizacao.cep) , (MicroEmpresasFechadasPorAno.CNAE_FISCAL_PRINCIPAL == dados.empresa.cnae)).first()


    if cnaesAbertos is None:
        nCnaesAbertos = 0

    else: 
        nCnaesAbertos = cnaesAbertos.EmpresasSimilaresAbertas

    if cnaesFechados is None:
        nCnaesFechados = 0
    
    else:
        nCnaesFechados = cnaesFechados.EmpresasSimilaresFechadas

    print(municObservado.Nome_Mun)
    feature_names = [
        'CNAE FISCAL PRINCIPAL',
        'CEP',
        'UF',
        'NATUREZA JURÍDICA',
        'QUALIFICAÇÃO DO RESPONSÁVEL',
        'FLAGSIMPLES',
        'FLAGMEI',
        'CÓDIGO_DO_MUNICÍPIO_IBGE',
        'PIB_2016',
        'PIB_2017',
        'PIB_2018',
        'PIB_2019',
        'PIB_2020',
        'PIB_2021',
        'Quant_Benificiarios',
        'Inss_Pagou_2022',
        'INSS_Ticket_Medio',
        'PIB_Medio',
        'PIB_Delta_Abs',
        'PIB_Cresc',
        'População_Masc_2021',
        'População_Fem_2021',
        'De_0_a_4_anos',
        'De_5_a_9_anos',
        'De_10_a_14_anos',
        'De_15_a_19_anos',
        'De_20_a_24_anos',
        'De_25_a_29_anos',
        'De_30_a_34_anos',
        'De_35_a_39_anos',
        'De_40_a_44_anos',
        'De_45_a_49_anos',
        'De_50_a_54_anos',
        'De_55_a_59_anos',
        'De_60_a_64_anos',
        'De_65_a_69_anos',
        'De_70_a_74_anos',
        'De_80_anos_ou_mais',
        'De_75_a_79_anos',
        'Pib_2016_Corrigido',
        'PIB_Delta_Corr',
        'PIB_Cresc_Corr',
        'POP_22',
        'EmpresasSimilaresAbertas',
        'EmpresasSimilaresFechadas'
    ]

# Crie um DataFrame em vez de numpy array
    inputModelo = pd.DataFrame([[
        dados.empresa.cnae,
        dados.localizacao.cep,
        municObservado.UF,
        dados.empresa.naturezaJuridica,
        dados.empresa.qualificacaoDoResponsavel,
        "S",
        valor_mei,
        cdMunic,
        municObservado.PIB_2016,
        municObservado.PIB_2017,
        municObservado.PIB_2018,
        municObservado.PIB_2019,
        municObservado.PIB_2020,
        municObservado.PIB_2021,
        municObservado.Quant_Benificiarios,
        municObservado.Inss_Pagou_2022,
        municObservado.INSS_Ticket_Medio,
        municObservado.PIB_Medio,
        municObservado.PIB_Delta_Abs,
        municObservado.PIB_Cresc,
        municObservado.População_Masc_2021,
        municObservado.População_Fem_2021,
        municObservado.De_0_a_4_anos,
        municObservado.De_5_a_9_anos,
        municObservado.De_10_a_14_anos,
        municObservado.De_15_a_19_anos,
        municObservado.De_20_a_24_anos,
        municObservado.De_25_a_29_anos,
        municObservado.De_30_a_34_anos,
        municObservado.De_35_a_39_anos,
        municObservado.De_40_a_44_anos,
        municObservado.De_45_a_49_anos,
        municObservado.De_50_a_54_anos,
        municObservado.De_55_a_59_anos,
        municObservado.De_60_a_64_anos,
        municObservado.De_65_a_69_anos,
        municObservado.De_70_a_74_anos,
        municObservado.De_80_anos_ou_mais,
        municObservado.De_75_a_79_anos,
        municObservado.Pib_2016_Corrigido,
        municObservado.PIB_Delta_Corr,
        municObservado.PIB_Cresc_Corr,
        municObservado.POP_22,
        nCnaesAbertos,
        nCnaesFechados
    ]], columns=feature_names)

    try:
        score_calculado = predict_viabilidade(inputModelo)
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

    '''detalhes_mock = { - explainable IA - Passo futuro
        "analise_localizacao": f"O bairro {dados.localizacao.bairro} possui alto fluxo para o CNAE {dados.empresa.cnae}.",
        "analise_mercado": "Baixa saturação de concorrentes na região.",
        "analise_economica": f"Capital de R$ {dados.empresa.capitalInicial} é adequado para o início.",
        "fatores_risco": ["Variação cambial", "Reformas na rua prevista"],
        "recomendacoes": ["Investir em marketing local", "Contratar 2 funcionários"]
    }'''
    
    nova_analise = Viabilidade(
        user_id=user.id,
        cep=dados.localizacao.cep,
        cidade=cdMunic,
        uf=municObservado.UF,
        cnae=dados.empresa.cnae,
        is_mei=dados.empresa.isMei,
        pontuacao=score_calculado
    )

    db.add(nova_analise)
    db.commit()
    db.refresh(nova_analise)
    
    return ViabilidadeResponse(
        status="success",
        message="Análise de viabilidade realizada com sucesso",
        data=DadosViabilidadeResponse(
            viabilidade_id=nova_analise.id,
            data_analise=nova_analise.data_analise,
            resultado=ResultadoViabilidade(
                pontuacao=nova_analise.pontuacao,
                detalhes=DetalhesResultado(
                    analise_localizacao=nova_analise.cep
                )
            ),
        ),
        code=200
    )
