drop table if exists ReceitaFederal..DadosEmpresasParaModeloV2;

select 
	t1.*
      , floor([DATA DE INÍCIO ATIVIDADE]/10000) as ANOABERTURA
      , t2.[POPULAÇÃO_ESTIMADA]
      , t2.[CD_MUNIC_INT]
      , t2.[PIB_2010]
      , t2.[PIB_2011]
      , t2.[PIB_2012]
      , t2.[PIB_2013]
      , t2.[PIB_2014]
      , t2.[PIB_2015]
      , t2.[PIB_2016]
      , t2.[PIB_2017]
      , t2.[PIB_2018]
      , t2.[PIB_2019]
      , t2.[PIB_2020]
      , t2.[PIB_2021]
      , t2.[INSS_QTD_25]
      , t2.[INSS_VLR_25]
      , t2.[NivelAlfabetizacao]
      , t3.taxaSelicAbertura
      , t4.EmpresasSimilaresAbertas
      , CASE 
            WHEN [SITUAÇÃO CADASTRAL] > 2 AND MesesAteSituacaoAtual < 48 THEN 1 -- 1 Morte prematura
            WHEN [SITUAÇÃO CADASTRAL] < 3 and IdadeCadastroEmMeses >= 48 THEN 2 -- 0 Viavel
            WHEN [SITUAÇÃO CADASTRAL] > 2 AND MesesAteSituacaoAtual >= 48 THEN 1 -- 0 Viavel
            WHEN [SITUAÇÃO CADASTRAL] < 3 AND MesesAteSituacaoAtual < 48 THEN 0 -- 2 Em processo
        end as ClassicacaoDeViabilidada
into ReceitaFederal..DadosEmpresasParaModeloV2
from (
		select
          t1.[CNPJ BÁSICO]
          , [SITUAÇÃO CADASTRAL]
          ,[DATA SITUAÇÃO CADASTRAL]
          ,[DATA DE INÍCIO ATIVIDADE]
          ,[CNAE FISCAL PRINCIPAL]
          ,[CEP]
          ,t1.[UF]
          ,[NATUREZA JURÍDICA]
          ,[QUALIFICAÇÃO DO RESPONSÁVEL]
          ,[PORTE DA EMPRESA]
            , CASE 
                WHEN [DATA SITUAÇÃO CADASTRAL] >= 19000101 
                     AND [DATA SITUAÇÃO CADASTRAL] <= 21000101
                     AND [DATA DE INÍCIO ATIVIDADE] >= 19000101 
                     AND [DATA DE INÍCIO ATIVIDADE] <= 21000101
                     AND LEN(CAST([DATA SITUAÇÃO CADASTRAL] AS VARCHAR(8))) = 8
                     AND LEN(CAST([DATA DE INÍCIO ATIVIDADE] AS VARCHAR(8))) = 8
                     AND TRY_CONVERT(date, CONVERT(varchar(8), [DATA SITUAÇÃO CADASTRAL]), 112) IS NOT NULL
                     AND TRY_CONVERT(date, CONVERT(varchar(8), [DATA DE INÍCIO ATIVIDADE]), 112) IS NOT NULL
                THEN DATEDIFF(
                    DAY, 
                    TRY_CONVERT(date, CONVERT(varchar(8), [DATA DE INÍCIO ATIVIDADE]), 112),
                    TRY_CONVERT(date, CONVERT(varchar(8), [DATA SITUAÇÃO CADASTRAL]), 112)
                ) / 30 
                ELSE NULL 
            END AS MesesAteSituacaoAtual

            , CASE 
                WHEN [DATA DE INÍCIO ATIVIDADE] >= 19000101 
                     AND [DATA DE INÍCIO ATIVIDADE] <= 21000101
                     AND LEN(CAST([DATA DE INÍCIO ATIVIDADE] AS VARCHAR(8))) = 8
                     AND TRY_CONVERT(date, CONVERT(varchar(8), [DATA DE INÍCIO ATIVIDADE]), 112) IS NOT NULL
                THEN DATEDIFF(
                    DAY, 
                    TRY_CONVERT(date, CONVERT(varchar(8), [DATA DE INÍCIO ATIVIDADE]), 112),
                    '2025-10-14'
                ) / 30 
                ELSE NULL 
            END AS IdadeCadastroEmMeses
          , CASE
				WHEN [DATA DE OPÇÃO PELO SIMPLES] IS NULL THEN 'N' 
				WHEN [DATA DE OPÇÃO PELO SIMPLES] = 0 THEN 'N'
				WHEN [DATA DE OPÇÃO PELO SIMPLES] IS NOT NULL THEN 'S'
			END AS FLAGSIMPLES
		   , CASE
				WHEN [DATA DE OPÇÃO PELO MEI] IS NULL THEN 'N'
				WHEN [DATA DE OPÇÃO PELO MEI] = 0 THEN 'N'
				WHEN [DATA DE OPÇÃO PELO MEI] IS NOT NULL THEN 'S'
			END AS FLAGMEI
            , [OPÇÃO PELO SIMPLES] as SIMPLESATIVO
			, [OPÇÃO PELO MEI] AS MEIATIVO
            , t2.CÓDIGO_DO_MUNICÍPIO_IBGE
		from ReceitaFederal..EmpresasNacionaisPeriodo t1
		left join ReceitaFederal..CodMunicipiosRF t2 on t1.MUNICÍPIO = t2.[CÓDIGO_DO_MUNICÍPIO_TOM]
        left join ReceitaFederal..Simples t3 on t1.[CNPJ BÁSICO] = t3.[CNPJ BÁSICO]
) t1
left join ReceitaFederal..DadosMunic t2 on t1.CÓDIGO_DO_MUNICÍPIO_IBGE = t2.CD_MUNIC_INT
left join ReceitaFederal..TaxaSelicAbertura t3 ON floor([DATA DE INÍCIO ATIVIDADE]/10000) = t3.Ano 
left join ReceitaFederal..MICROEMPRESASABERTASPORANO t4 on t1.CEP = t4.CEP AND t1.[CNAE FISCAL PRINCIPAL] = t4.[CNAE FISCAL PRINCIPAL] AND floor([DATA DE INÍCIO ATIVIDADE]/10000) = t4.ANOABERTURA
left join ReceitaFederal..MICROEMPRESASFECHADASSPORANO t5 on t1.CEP = t4.CEP AND t1.[CNAE FISCAL PRINCIPAL] = t5.[CNAE FISCAL PRINCIPAL] AND (floor([DATA DE INÍCIO ATIVIDADE]/10000)-1) = t5.ANOBAIXA
where ([PORTE DA EMPRESA] < 3 OR [PORTE DA EMPRESA] is null) and (MEIATIVO like 'N') and (([SITUAÇÃO CADASTRAL] > 2 and MesesAteSituacaoAtual > 1) or [SITUAÇÃO CADASTRAL] < 3) and (IdadeCadastroEmMeses > 3);
 -- filtramos qualquer CNPJ que não seja de micro-empresa, retira MEIs, retira empresas com menos de 3 meses de cadastro, retira empresas que faliram com menos de 2 meses


