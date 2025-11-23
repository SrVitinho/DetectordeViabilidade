import requests
from fastapi import APIRouter, status, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from functools import lru_cache

router = APIRouter(
    prefix='/api/helpers',
    tags=['Helpers - Listas Auxiliares']
)

class ItemAuxiliar(BaseModel):
    codigo: str
    descricao: str
    observacoes: Optional[str] = None
    
QUALIFICACOES_FIXAS = [
  {"codigo": "05", "descricao": "Administrador"},
  { "codigo": "08", "descricao": "Conselheiro de Administração" },
  { "codigo": "09", "descricao": "Curador" },
  { "codigo": "10", "descricao": "Diretor" },
  { "codigo": "11", "descricao": "Interventor" },
  { "codigo": "12", "descricao": "Inventariante" },
  { "codigo": "13", "descricao": "Liquidante" },
  { "codigo": "14", "descricao": "Mãe" },
  { "codigo": "15", "descricao": "Pai" },
  { "codigo": "16", "descricao": "Presidente" },
  { "codigo": "17", "descricao": "Procurador" },
  { "codigo": "18", "descricao": "Secretário" },
  { "codigo": "19", "descricao": "Síndico (Condomínio ou Falência)" },
  { "codigo": "20", "descricao": "Sociedade Consorciada" },
  { "codigo": "21", "descricao": "Sociedade Filiada" },
  { "codigo": "22", "descricao": "Sócio" },
  { "codigo": "23", "descricao": "Sócio Capitalista" },
  { "codigo": "24", "descricao": "Sócio Comanditado" },
  { "codigo": "25", "descricao": "Sócio Comanditário" },
  { "codigo": "26", "descricao": "Sócio de Indústria" },
  { "codigo": "28", "descricao": "Sócio-Gerente" },
  { "codigo": "29", "descricao": "Sócio Incapaz ou Relat.Incapaz (exceto menor)" },
  { "codigo": "30", "descricao": "Sócio Menor (Assistido/Representado)" },
  { "codigo": "31", "descricao": "Sócio Ostensivo" },
  { "codigo": "32", "descricao": "Tabelião" },
  { "codigo": "33", "descricao": "Tesoureiro" },
  { "codigo": "34", "descricao": "Titular de Empresa Individual Imobiliária" },
  { "codigo": "35", "descricao": "Tutor" },
  { "codigo": "37", "descricao": "Sócio Pessoa Jurídica Domiciliado no Exterior" },
  { "codigo": "38", "descricao": "Sócio Pessoa Física Residente ou Domiciliado no Exterior" },
  { "codigo": "39", "descricao": "Diplomata" },
  { "codigo": "40", "descricao": "Cônsul" },
  { "codigo": "41", "descricao": "Representante de Organização Internacional" },
  { "codigo": "42", "descricao": "Oficial de Registro" },
  { "codigo": "43", "descricao": "Responsável" },
  { "codigo": "46", "descricao": "Ministro de Estado das Relações Exteriores" },
  { "codigo": "47", "descricao": "Sócio Pessoa Física Residente no Brasil" },
  { "codigo": "48", "descricao": "Sócio Pessoa Jurídica Domiciliado no Brasil" },
  { "codigo": "49", "descricao": "Sócio-Administrador" },
  { "codigo": "50", "descricao": "Empresário" },
  { "codigo": "51", "descricao": "Candidato a Cargo Político Eletivo" },
  { "codigo": "52", "descricao": "Sócio com Capital" },
  { "codigo": "53", "descricao": "Sócio sem Capital" },
  { "codigo": "54", "descricao": "Fundador" },
  { "codigo": "55", "descricao": "Sócio-Diretor" },
  { "codigo": "56", "descricao": "Sócio-Presidente" },
  { "codigo": "57", "descricao": "Sócio Especial" },
  { "codigo": "58", "descricao": "Titular de EIRELI" },
  { "codigo": "59", "descricao": "Produtor Rural" },
  { "codigo": "60", "descricao": "Consul Honorário" },
  { "codigo": "63", "descricao": "Cotas em Tesouraria" },
  { "codigo": "65", "descricao": "Titular Pessoa Física Residente ou Domiciliado no Brasil" },
  { "codigo": "66", "descricao": "Titular Pessoa Física Residente ou Domiciliado no Exterior" },
  { "codigo": "67", "descricao": "Titular Pessoa Física Incapaz ou Relativamente Incapaz (exceto menor)" },
  { "codigo": "68", "descricao": "Titular Pessoa Física Menor (Assistido/Representado)" },
  { "codigo": "69", "descricao": "Beneficiário Final" },
  { "codigo": "70", "descricao": "Administrador Residente ou Domiciliado no Exterior" },
  { "codigo": "71", "descricao": "Conselheiro de Administração Residente ou Domiciliado no Exterior" },
  { "codigo": "72", "descricao": "Diretor Residente ou Domiciliado no Exterior" },
  { "codigo": "73", "descricao": "Presidente Residente ou Domiciliado no Exterior" },
  { "codigo": "74", "descricao": "Sócio-Administrador Residente ou Domiciliado no Exterior" },
  { "codigo": "75", "descricao": "Fundador Residente ou Domiciliado no Exterior" },
  { "codigo": "78", "descricao": "Titular Pessoa Jurídica Domiciliada no Brasil" },
  { "codigo": "79", "descricao": "Titular Pessoa Jurídica Domiciliada no Exterior" }
]

NATUREZA_JURIDICA = [
    { "codigo": "101-5", "descricao": "Órgão Público do Poder Executivo Federal" },
    { "codigo": "102-3", "descricao": "Órgão Público do Poder Executivo Estadual ou do Distrito Federal" },
    { "codigo": "103-1", "descricao": "Órgão Público do Poder Executivo Municipal" },
    { "codigo": "104-0", "descricao": "Órgão Público do Poder Legislativo Federal" },
    { "codigo": "105-8", "descricao": "Órgão Público do Poder Legislativo Estadual ou do Distrito Federal" },
    { "codigo": "106-6", "descricao": "Órgão Público do Poder Legislativo Municipal" },
    { "codigo": "107-4", "descricao": "Órgão Público do Poder Judiciário Federal" },
    { "codigo": "108-2", "descricao": "Órgão Público do Poder Judiciário Estadual" },
    { "codigo": "110-4", "descricao": "Autarquia Federal" },
    { "codigo": "111-2", "descricao": "Autarquia Estadual ou do Distrito Federal" },
    { "codigo": "112-0", "descricao": "Autarquia Municipal" },
    { "codigo": "113-9", "descricao": "Fundação Federal" },
    { "codigo": "114-7", "descricao": "Fundação Estadual ou do Distrito Federal" },
    { "codigo": "115-5", "descricao": "Fundação Municipal" },
    { "codigo": "116-3", "descricao": "Órgão Público Autônomo da União" },
    { "codigo": "117-1", "descricao": "Órgão Público Autônomo Estadual ou do Distrito Federal" },
    { "codigo": "118-0", "descricao": "Órgão Público Autônomo Municipal" },
    { "codigo": "201-1", "descricao": "Empresa Pública" },
    { "codigo": "203-8", "descricao": "Sociedade de Economia Mista" },
    { "codigo": "204-6", "descricao": "Sociedade Anônima Aberta" },
    { "codigo": "205-4", "descricao": "Sociedade Anônima Fechada" },
    { "codigo": "206-2", "descricao": "Sociedade Empresária Limitada" },
    { "codigo": "207-6", "descricao": "Sociedade Empresária em Nome Coletivo" },
    { "codigo": "208-9", "descricao": "Sociedade Empresária em Comandita Simples" },
    { "codigo": "209-7", "descricao": "Sociedade Empresária em Comandita por Ações" },
    { "codigo": "210-0", "descricao": "Sociedade Mercantil de Capital e Indústria (extinta pelo NCC/2002)" },
    { "codigo": "212-7", "descricao": "Sociedade Empresária em Conta de Participação" },
    { "codigo": "213-5", "descricao": "Empresário (Individual)" },
    { "codigo": "214-3", "descricao": "Cooperativa" },
    { "codigo": "215-1", "descricao": "Consórcio de Sociedades" },
    { "codigo": "216-0", "descricao": "Grupo de Sociedades" },
    { "codigo": "217-8", "descricao": "Estabelecimento, no Brasil, de Sociedade Estrangeira" },
    { "codigo": "219-4", "descricao": "Estabelecimento, no Brasil, de Empresa Binacional Argentino-Brasileira" },
    { "codigo": "220-8", "descricao": "Entidade Binacional Itaipu" },
    { "codigo": "221-6", "descricao": "Empresa Domiciliada no Exterior" },
    { "codigo": "222-4", "descricao": "Clube/Fundo de Investimento" },
    { "codigo": "223-2", "descricao": "Sociedade Simples Pura" },
    { "codigo": "224-0", "descricao": "Sociedade Simples Limitada" },
    { "codigo": "225-9", "descricao": "Sociedade em Nome Coletivo" },
    { "codigo": "226-7", "descricao": "Sociedade em Comandita Simples" },
    { "codigo": "227-5", "descricao": "Sociedade Simples em Conta de Participação" },
    { "codigo": "230-5", "descricao": "Empresa Individual de Responsabilidade Limitada" },
    { "codigo": "303-4", "descricao": "Serviço Notarial e Registral (Cartório)" },
    { "codigo": "304-2", "descricao": "Organização Social" },
    { "codigo": "305-0", "descricao": "Organização da Sociedade Civil de Interesse Público (Oscip)" },
    { "codigo": "306-9", "descricao": "Outras Formas de Fundações Mantidas com Recursos Privados" },
    { "codigo": "307-7", "descricao": "Serviço Social Autônomo" },
    { "codigo": "308-5", "descricao": "Condomínio Edilícios" },
    { "codigo": "309-3", "descricao": "Unidade Executora (Programa Dinheiro Direto na Escola)" },
    { "codigo": "310-7", "descricao": "Comissão de Conciliação Prévia" },
    { "codigo": "311-5", "descricao": "Entidade de Mediação e Arbitragem" },
    { "codigo": "312-3", "descricao": "Partido Político" },
    { "codigo": "313-1", "descricao": "Entidade Sindical" },
    { "codigo": "320-4", "descricao": "Estabelecimento, no Brasil, de Fundação ou Associação Estrangeiras" },
    { "codigo": "321-2", "descricao": "Fundação ou Associação Domiciliada no Exterior" },
    { "codigo": "399-9", "descricao": "Outras Formas de Associação" },
    { "codigo": "401-4", "descricao": "Empresa Individual Imobiliária" },
    { "codigo": "402-2", "descricao": "Segurado Especial" },
    { "codigo": "408-1", "descricao": "Contribuinte individual" },
    { "codigo": "500-2", "descricao": "Organização Internacional e Outras Instituições Extraterritoriais" }
]

@lru_cache(maxsize=1)
def fetch_ibge_cnaes():
    try:
        response = requests.get("https://servicodados.ibge.gov.br/api/v2/cnae/classes")
        response.raise_for_status()
        data = response.json()
        
        lista = []
        
        cortes = [
            "Esta classe compreende ainda",
            "Esta classe NÃO compreende",
            "\r"
        ]
        
        for item in data:
            obs_lista = item.get('observacoes', [])
            obs_texto = " ".join(obs_lista) if isinstance(obs_lista, list) else str(obs_lista)
            
            for corte in cortes:
                if corte in obs_texto:
                    obs_texto = obs_texto.split(corte)[0]
            
            lista.append({
                "codigo": item['id'],
                "descricao": item['descricao'],
                "observacoes": obs_texto
            })
        
        return lista
    except Exception as e:
        print(f"Erro ao buscar CNAEs do IBGE: {e}")
        return []

@router.get("/qualificacoes", response_model=List[ItemAuxiliar])
async def get_qualificacoes():
    return QUALIFICACOES_FIXAS

@router.get("/naturezas", response_model=List[ItemAuxiliar])
async def get_naturezas():
    return NATUREZA_JURIDICA

@router.get("/cnaes", response_model=List[ItemAuxiliar])
async def get_cnaes():
    cnaes = fetch_ibge_cnaes()
    if not cnaes:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Serviço do IBGE indisponível no momento.")
    
    return cnaes