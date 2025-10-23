SET LOCK_TIMEOUT 0;
SET QUERY_GOVERNOR_COST_LIMIT 0

drop table if exists ReceitaFederal..EmpresasNacionaisPeriodo
select
    t1.*,
    t2.[NATUREZA JURÍDICA],
    t2.[QUALIFICAÇÃO DO RESPONSÁVEL],
    t2.[CAPITAL SOCIAL DA EMPRESA],
    t2.[PORTE DA EMPRESA]
INTO ReceitaFederal.dbo.EmpresasNacionaisPeriodo
from
    (
        SELECT 
            [CNPJ BÁSICO]
            ,[CNPJ ORDEM]
            ,[CNPJ DV]
            ,[IDENTIFICADOR MATRIZ/FILIAL]
            ,[SITUAÇÃO CADASTRAL]
            ,[DATA SITUAÇÃO CADASTRAL]
            ,[DATA DE INÍCIO ATIVIDADE]
            ,[CNAE FISCAL PRINCIPAL]
            ,[TIPO DE LOGRADOURO]
            ,[LOGRADOURO]
            ,[NÚMERO]
            ,[COMPLEMENTO]
            ,[BAIRRO]
            ,[CEP]
            ,[UF]
            ,[MUNICÍPIO]
        FROM ReceitaFederal..Estabelecimentos
        WHERE (([DATA DE INÍCIO ATIVIDADE] BETWEEN 20100101 AND 20200101) OR ([DATA DE INÍCIO ATIVIDADE] > 20220101)) AND ([PAIS] IS NULL OR [PAIS] IN (0, 105, 106))
    ) t1
left join ReceitaFederal..Empresas t2 ON t1.[CNPJ BÁSICO] = t2.[CNPJ BÁSICO];