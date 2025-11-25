from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated
import json
import requests
import pandas as pd

from database import SessionLocal
from models import Viabilidade, User, DadosMunic, MicroEmpresasAbertasPorAno, MicroEmpresasFechadasPorAno
from  Viabilidade.viabilidadeBase import ViabilidadeRequest, ViabilidadeResponse, DetalhesResultado, ResultadoViabilidade, DadosViabilidadeResponse, LocalizacaoResponse, HistoricoItem, HistoricoResponse
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
    dados_endereco = {}
    cdMunic = ""
    
    try:
        cep_filtrado = dados.localizacao.cep.replace("-", "").replace(".", "").strip()
            
        r = requests.get(f"https://cep.awesomeapi.com.br/json/{cep_filtrado}")
        
        if r.status_code != 200:
            raise Exception("CEP não encontrado na API.")
        
        api_data = r.json()
        
        if "city_ibge" not in api_data:
            raise Exception("CEP válido, mas sem código IBGE associado")
        
        cdMunic = api_data["city_ibge"]
        
        rua = api_data.get("address", "")
        bairro = api_data.get("district", "")
        
        dados_endereco = {
            "cep": api_data.get("cep", cep_filtrado),
            "rua": rua if rua else None,
            "bairro": bairro if bairro else None,
            "cidade": api_data.get("city"),
            "uf": api_data.get("state"),
            "lat": api_data.get("lat"),
            "lng": api_data.get("lng")
        }
        
        print(f"Município IBGE: {cdMunic} | Lat: {dados_endereco['lat']}| Lng: {dados_endereco['lng']}")

    except Exception as err:
            print(err)
            return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "CEP inválido, não encontrado ou serviço indisponível.",
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
    
    if not municObservado:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "error", "message": "Dados do município não encontrados na base interna.", "code": 404}
        )

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

    e_viavel = score_calculado >= 0.6 
    
    nova_analise = Viabilidade(
        user_id=user.id,
        cep=cep_filtrado,
        cidade=cdMunic,
        uf=municObservado.UF,
        rua=dados_endereco.get("rua"),
        bairro=dados_endereco.get("bairro"),
        capital_inicial=dados.empresa.capitalInicial,
        viavel=e_viavel,
        
        analise_localizacao=f"Análise para o CEP {cep_filtrado}", 
        analise_mercado="Análise pendente...",
        analise_economica="Análise pendente...",
        fatores_risco="[]",
        recomendacoes="[]",
        
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
            
            localizacao=LocalizacaoResponse(
                cep=dados_endereco["cep"],
                rua=dados_endereco["rua"],
                bairro=dados_endereco["bairro"],
                cidade=dados_endereco["cidade"],
                uf=dados_endereco["uf"],
                latitude=dados_endereco["lat"],
                longitude=dados_endereco["lng"]
            ),
            
            resultado=ResultadoViabilidade(
                pontuacao=nova_analise.pontuacao,
                detalhes=DetalhesResultado(
                    analise_localizacao=cep_filtrado
                )
            ),
        ),
        code=200
    )

@router.get("/historico", response_model=HistoricoResponse)
async def get_historico_usuario(
    user: user_dependency,
    db: db_dependency,
):
    resultados = db.query(Viabilidade, DadosMunic.Nome_Mun).outerjoin(DadosMunic, Viabilidade.cidade == DadosMunic.ID_MUN).filter(Viabilidade.user_id == user.id).order_by(Viabilidade.data_analise.desc()).all()
        
    lista_formatada = []
    
    for viabilidade, nome_cidade in resultados:
        
        partes_endereco = []
        
        if viabilidade.rua:
            partes_endereco.append(viabilidade.rua)
        
        if viabilidade.bairro:
            partes_endereco.append(viabilidade.bairro)
            
        cidade_display = nome_cidade if nome_cidade else viabilidade.cidade
        partes_endereco.append(f"{cidade_display} - {viabilidade.uf}")
        
        local_completo = ", ".join(partes_endereco)
        
        lista_formatada.append(
            HistoricoItem(
                id=viabilidade.id,
                cnae=viabilidade.cnae,
                local=local_completo,
                pontuacao=viabilidade.pontuacao,
                viavel=viabilidade.viavel if viabilidade.viavel is not None else (viabilidade.pontuacao >= 0.6),
                data_analise=viabilidade.data_analise
            )
        )
        
    return HistoricoResponse(
        status="success",
        message=f"{len(lista_formatada)} análises encontradas para o usuário {user.name}.",
        data=lista_formatada,
        code=200
    )
    
@router.get("/historico/{viabilidade_id}", response_model=ViabilidadeResponse)
async def get_analise_detalhes(
    viabilidade_id: int,
    user: user_dependency,
    db: db_dependency,
):
    analise = db.query(Viabilidade).filter(
        Viabilidade.id == viabilidade_id,
        Viabilidade.user_id == user.id
    ).first()
    
    if not analise:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "message": "Análise de viabilidade não encontrada no histórico.",
                "code": 404
            }
        )
    
    nome_cidade = str(analise.cidade)
    if analise.cidade:
        municipio_obj = db.query(DadosMunic).filter(DadosMunic.ID_MUN == str(analise.cidade)).first()
        if municipio_obj:
            nome_cidade = municipio_obj.Nome_Mun
            
    try:
        fatores_lista = json.loads(analise.fatores_risco) if analise.fatores_risco else []
        recomendacoes_lista = json.loads(analise.recomendacoes) if analise.recomendacoes else []
    except Exception:
        fatores_lista = []
        recomendacoes_lista = []
        
        lat_api = None
    lng_api = None
    rua_api = getattr(analise, 'rua', None)
    bairro_api = getattr(analise, 'bairro', None)
    cidade_api = str(analise.cidade)
    uf_api = analise.uf

    if analise.cep:
        try:
            cep_limpo = analise.cep.replace("-", "").replace(".", "").strip()
            # Timeout curto para não travar a resposta se a API cair
            r = requests.get(f"https://cep.awesomeapi.com.br/json/{cep_limpo}", timeout=3)
            
            if r.status_code == 200:
                data_api = r.json()
                lat_api = data_api.get("lat")
                lng_api = data_api.get("lng")
                
                # Aproveita para preencher rua/bairro se no banco estiver vazio
                if not rua_api:
                    rua_api = data_api.get("address")
                if not bairro_api:
                    bairro_api = data_api.get("district")
                
                # Atualiza nome da cidade (para não mostrar código IBGE)
                if data_api.get("city"):
                    cidade_api = data_api.get("city")
                    
        except Exception as e:
            print(f"Erro ao buscar coordenadas para histórico: {e}")
            # Se der erro, segue a vida com os dados que tem no banco
        
    local_response = LocalizacaoResponse(
        cep=analise.cep,
        cidade=nome_cidade,
        uf=analise.uf,
        rua=getattr(analise, 'rua', None),    
        bairro=getattr(analise, 'bairro', None), 
        latitude=lat_api, 
        longitude=lng_api 
    )
    
    return ViabilidadeResponse(
        status="success",
        message="Detalhes recuperados.",
        data=DadosViabilidadeResponse(
            viabilidade_id=analise.id,
            data_analise=analise.data_analise,
            localizacao=local_response,
            resultado=ResultadoViabilidade(
                pontuacao=analise.pontuacao,
                detalhes=DetalhesResultado(
                    analise_localizacao=int(analise.cep.replace("-","").replace(".","")) if analise.cep else 0
                )
            )
        ),
        code=200
    )
    
@router.delete("/historico/{viabilidade_id}", response_model=ViabilidadeResponse)
async def deletar_analise(
    viabilidade_id: int,
    user: user_dependency,
    db: db_dependency
):
    analise_para_deletar = db.query(Viabilidade).filter(
        Viabilidade.id == viabilidade_id,
        Viabilidade.user_id == user.id
    ).first()

    if not analise_para_deletar:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "error",
                "message": "Análise não encontrada ou você não tem permissão para excluí-la.",
                "code": 404
            }
        )

    try:
        db.delete(analise_para_deletar)
        db.commit()

        return ViabilidadeResponse(
            status="success",
            message=f"Análise {viabilidade_id} excluída com sucesso.",
            data=None,
            code=200
        )

    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": f"Erro ao tentar excluir: {str(e)}",
                "code": 500
            }
        )