DROP TABLE IF EXISTS #SubqueryT1;

SELECT
    t1.[CNPJ BÁSICO],
    [SITUAÇÃO CADASTRAL],
    [DATA SITUAÇÃO CADASTRAL],
    [DATA DE INÍCIO ATIVIDADE],
    [CNAE FISCAL PRINCIPAL],
    [CEP],
    t1.[UF],
    [NATUREZA JURÍDICA],
    [QUALIFICAÇÃO DO RESPONSÁVEL],
    [PORTE DA EMPRESA],
    t1.ANOABERTURA,
    
    CASE 
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
    END AS MesesAteSituacaoAtual,
    
    CASE 
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
    END AS IdadeCadastroEmMeses,

    CASE
        WHEN t3.[DATA DE OPÇÃO PELO SIMPLES] IS NULL THEN 'N' 
        WHEN t3.[DATA DE OPÇÃO PELO SIMPLES] = 0 THEN 'N'
        WHEN t3.[DATA DE OPÇÃO PELO SIMPLES] IS NOT NULL THEN 'S'
    END AS FLAGSIMPLES,

    CASE
        WHEN t3.[DATA DE OPÇÃO PELO MEI] IS NULL THEN 'N'
        WHEN t3.[DATA DE OPÇÃO PELO MEI] = 0 THEN 'N'
        WHEN t3.[DATA DE OPÇÃO PELO MEI] IS NOT NULL THEN 'S'
    END AS FLAGMEI,
    
    t3.[OPÇÃO PELO SIMPLES] as SIMPLESATIVO,
    t3.[OPÇÃO PELO MEI] AS MEIATIVO,
    t2.CÓDIGO_DO_MUNICÍPIO_IBGE

INTO #SubqueryT1
FROM ReceitFederal..EmpresasNacionaisPeriodoAmostra t1
LEFT JOIN ReceitFederal..CodMunicipiosRF t2 
    ON t1.MUNICÍPIO = t2.[CÓDIGO_DO_MUNICÍPIO_TOM]
LEFT JOIN ReceitFederal..Simples t3 
    ON t1.[CNPJ BÁSICO] = t3.[CNPJ BÁSICO];

CREATE INDEX idx_temp1 ON #SubqueryT1(
    ANOABERTURA,
    CEP, 
    [CNAE FISCAL PRINCIPAL],
    CÓDIGO_DO_MUNICÍPIO_IBGE
) INCLUDE ([PORTE DA EMPRESA], MEIATIVO, [SITUAÇÃO CADASTRAL], MesesAteSituacaoAtual, IdadeCadastroEmMeses);


CREATE INDEX idx_temp1 ON #SubqueryT1(
    ANOABERTURA,
    [CNAE FISCAL PRINCIPAL],
    CÓDIGO_DO_MUNICÍPIO_IBGE
) INCLUDE (
    CEP,
    [PORTE DA EMPRESA], 
    MEIATIVO, 
    [SITUAÇÃO CADASTRAL], 
    MesesAteSituacaoAtual, 
    IdadeCadastroEmMeses
);

CREATE INDEX idx_temp1 ON #SubqueryT1(
    ANOABERTURA,
    [CNAE FISCAL PRINCIPAL],
    CÓDIGO_DO_MUNICÍPIO_IBGE
) INCLUDE (
    CEP,
    [PORTE DA EMPRESA], 
    MEIATIVO, 
    [SITUAÇÃO CADASTRAL], 
    MesesAteSituacaoAtual, 
    IdadeCadastroEmMeses
);


DROP TABLE IF EXISTS ReceitFederal..DadosEmpresasParaModeloV3;

SELECT 
    t1.[CNPJ BÁSICO],
    t1.[SITUAÇÃO CADASTRAL],
    t1.[DATA SITUAÇÃO CADASTRAL],
    t1.[DATA DE INÍCIO ATIVIDADE],
    t1.[CNAE FISCAL PRINCIPAL],
    t1.[CEP],
    t1.[UF],
    t1.[NATUREZA JURÍDICA],
    t1.[QUALIFICAÇÃO DO RESPONSÁVEL],
    t1.[PORTE DA EMPRESA],
    t1.MesesAteSituacaoAtual,
    t1.IdadeCadastroEmMeses,
    t1.FLAGSIMPLES,
    t1.FLAGMEI,
    t1.SIMPLESATIVO,
    t1.MEIATIVO,
    t1.CÓDIGO_DO_MUNICÍPIO_IBGE,
    t1.ANOABERTURA,
    t2.[PIB_2016],
    t2.[PIB_2017],
    t2.[PIB_2018],
    t2.[PIB_2019],
    t2.[PIB_2020],
    t2.[PIB_2021],
    t2.[Quant_Benificiarios],
    t2.[Inss_Pagou_2022],
    t2.[INSS_Ticket_Medio],
    t2.[PIB_Medio],
    t2.[PIB_Delta_Abs],
    t2.[PIB_Cresc],
    t2.[População_Masc_2021],
    t2.[População_Fem_2021],
    t2.[De_0_a_4_anos],
    t2.[De_5_a_9_anos],
    t2.[De_10_a_14_anos],
    t2.[De_15_a_19_anos],
    t2.[De_20_a_24_anos],
    t2.[De_25_a_29_anos],
    t2.[De_30_a_34_anos],
    t2.[De_35_a_39_anos],
    t2.[De_40_a_44_anos],
    t2.[De_45_a_49_anos],
    t2.[De_50_a_54_anos],
    t2.[De_55_a_59_anos],
    t2.[De_60_a_64_anos],
    t2.[De_65_a_69_anos],
    t2.[De_70_a_74_anos],
    t2.[De_80_anos_ou_mais],
    t2.[De_75_a_79_anos],
    t2.[Pib_2016_Corrigido],
    t2.[PIB_Delta_Corr],
    t2.[PIB_Cresc_Corr],
    t2.[POP_22],
    
    t4.EmpresasSimilaresAbertas,
    t5.EmpresasSimilaresFechadas,

    CASE 
        WHEN t1.[SITUAÇÃO CADASTRAL] > 2 AND t1.MesesAteSituacaoAtual < 24 THEN 1 -- morte prematura
        WHEN t1.[SITUAÇÃO CADASTRAL] < 3 AND t1.IdadeCadastroEmMeses >= 24 THEN 0 -- viavel 
        WHEN t1.[SITUAÇÃO CADASTRAL] > 2 AND t1.MesesAteSituacaoAtual >= 24 THEN 0 -- viavel
        WHEN t1.[SITUAÇÃO CADASTRAL] < 3 AND t1.MesesAteSituacaoAtual < 24 THEN 2
    END AS ClassicacaoDeViabilidada

INTO ReceitFederal..DadosEmpresasParaModeloV3
FROM #SubqueryT1 t1
LEFT JOIN ReceitFederal..DadosMunic t2 
    ON t1.CÓDIGO_DO_MUNICÍPIO_IBGE = t2.ID_MUN
LEFT JOIN ReceitFederal..MICROEMPRESASABERTASPORANO t4 
    ON t1.CEP = t4.CEP 
    AND t1.[CNAE FISCAL PRINCIPAL] = t4.[CNAE FISCAL PRINCIPAL] 
    AND t1.ANOABERTURA = t4.ANOABERTURA
LEFT JOIN ReceitFederal..MICROEMPRESASFECHADASSPORANO t5 
    ON t1.CEP = t5.CEP 
    AND t1.[CNAE FISCAL PRINCIPAL] = t5.[CNAE FISCAL PRINCIPAL] 
    AND (t1.ANOABERTURA - 1) = t5.ANOBAIXA
WHERE 
    (t1.[PORTE DA EMPRESA] < 3 OR t1.[PORTE DA EMPRESA] IS NULL) 
    AND (t1.MEIATIVO LIKE 'N') 
    AND ((t1.[SITUAÇÃO CADASTRAL] > 2 AND t1.MesesAteSituacaoAtual > 1) OR t1.[SITUAÇÃO CADASTRAL] < 3) 
    AND (t1.IdadeCadastroEmMeses > 3);