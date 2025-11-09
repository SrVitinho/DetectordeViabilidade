drop table if exists ReceitFederal..DadosEmpresasParaModeloV2;

select 
	t1.*
      , floor([DATA DE INÍCIO ATIVIDADE]/10000) as ANOABERTURA
      , t2.[PIB_2016]
      ,t2.[PIB_2017]
      ,t2.[PIB_2018]
      ,t2.[PIB_2019]
      ,t2.[PIB_2020]
      ,t2.[PIB_2021]
      ,t2.[Quant_Benificiarios]
      ,t2.[Inss_Pagou_2022]
      ,t2.[INSS_Ticket_Medio]
      ,t2.[PIB_Medio]
      ,t2.[PIB_Delta_Abs]
      ,t2.[PIB_Cresc]
      ,t2.[População_Masc_2021]
      ,t2.[População_Fem_2021]
      ,t2.[De_0_a_4_anos]
      ,t2.[De_5_a_9_anos]
      ,t2.[De_10_a_14_anos]
      ,t2.[De_15_a_19_anos]
      ,t2.[De_20_a_24_anos]
      ,t2.[De_25_a_29_anos]
      ,t2.[De_30_a_34_anos]
      ,t2.[De_35_a_39_anos]
      ,t2.[De_40_a_44_anos]
      ,t2.[De_45_a_49_anos]
      ,t2.[De_50_a_54_anos]
      ,t2.[De_55_a_59_anos]
      ,t2.[De_60_a_64_anos]
      ,t2.[De_65_a_69_anos]
      ,t2.[De_70_a_74_anos]
      ,t2.[De_80_anos_ou_mais]
      ,t2.[De_75_a_79_anos]
      ,t2.[Pib_2016_Corrigido]
      ,t2.[PIB_Delta_Corr]
      ,t2.[PIB_Cresc_Corr]
      ,t2.[POP_22]
      , t4.EmpresasSimilaresAbertas
      , t5.EmpresasSimilaresFechadas
      , CASE 
            WHEN [SITUAÇÃO CADASTRAL] > 2 AND MesesAteSituacaoAtual < 48 THEN 1 -- 1 Viavel
            WHEN [SITUAÇÃO CADASTRAL] < 3 and IdadeCadastroEmMeses >= 48 THEN 2 -- 2 Viavel
            WHEN [SITUAÇÃO CADASTRAL] > 2 AND MesesAteSituacaoAtual >= 48 THEN 1 -- 0 Viavel
            WHEN [SITUAÇÃO CADASTRAL] < 3 AND MesesAteSituacaoAtual < 48 THEN 0 -- 0 Em processo
        end as ClassicacaoDeViabilidada
into ReceitFederal..DadosEmpresasParaModeloV2
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
		from ReceitFederal..EmpresasNacionaisPeriodoAmostra t1
		left join ReceitFederal..CodMunicipiosRF t2 on t1.MUNICÍPIO = t2.[CÓDIGO_DO_MUNICÍPIO_TOM]
        left join ReceitFederal..Simples t3 on t1.[CNPJ BÁSICO] = t3.[CNPJ BÁSICO]
) t1
left join ReceitFederal..DadosMunic t2 on t1.CÓDIGO_DO_MUNICÍPIO_IBGE = t2.ID_MUN
left join ReceitFederal..MICROEMPRESASABERTASPORANO t4 on t1.CEP = t4.CEP AND t1.[CNAE FISCAL PRINCIPAL] = t4.[CNAE FISCAL PRINCIPAL] AND floor([DATA DE INÍCIO ATIVIDADE]/10000) = t4.ANOABERTURA
left join ReceitFederal..MICROEMPRESASFECHADASSPORANO t5 on t1.CEP = t5.CEP AND t1.[CNAE FISCAL PRINCIPAL] = t5.[CNAE FISCAL PRINCIPAL] AND (floor([DATA DE INÍCIO ATIVIDADE]/10000)-1) = t5.ANOBAIXA
where ([PORTE DA EMPRESA] < 3 OR [PORTE DA EMPRESA] is null) and (MEIATIVO like 'N') and (([SITUAÇÃO CADASTRAL] > 2 and MesesAteSituacaoAtual > 1) or [SITUAÇÃO CADASTRAL] < 3) and (IdadeCadastroEmMeses > 3);
 -- filtramos qualquer CNPJ que não seja de micro-empresa, retira MEIs, retira empresas com menos de 3 meses de cadastro, retira empresas que faliram com menos de 2 meses


