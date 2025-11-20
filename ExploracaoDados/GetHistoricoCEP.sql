drop table if exists ReceitaFederal..MICROEMPRESASABERTASPORANO;
SELECT distinct COUNT([CNPJ BÁSICO]) AS EmpresasSimilaresAbertas
      ,ANOABERTURA
      ,[CNAE FISCAL PRINCIPAL]
      ,[CEP]
  INTO ReceitaFederal..MICROEMPRESASABERTASPORANO
  FROM (
        select
            [CNPJ BÁSICO]
            , floor([DATA SITUAÇÃO CADASTRAL]/10000) as ANOABERTURA
            ,[CNAE FISCAL PRINCIPAL]
            ,[CEP]          
            ,[PORTE DA EMPRESA]
            ,[SITUAÇÃO CADASTRAL]
        from [ReceitaFederal].[dbo].[EmpresasNacionaisPeriodo]
       ) t1
  WHERE [PORTE DA EMPRESA] < 3 --MANTEM APENAS MICROEMPRESAS
  GROUP BY ANOABERTURA, [CNAE FISCAL PRINCIPAL], [CEP]


         
drop table if exists ReceitaFederal..MICROEMPRESASFECHADASSPORANO;
SELECT distinct COUNT([CNPJ BÁSICO]) AS EmpresasSimilaresFechadas
      ,ANOBAIXA
      ,[CNAE FISCAL PRINCIPAL]
      ,[CEP]
  INTO ReceitaFederal..MICROEMPRESASFECHADASSPORANO
  FROM (
        select
            [CNPJ BÁSICO]
            , floor([DATA SITUAÇÃO CADASTRAL]/10000) as ANOBAIXA
            ,[CNAE FISCAL PRINCIPAL]
            ,[CEP]          
            ,[PORTE DA EMPRESA]
            ,[SITUAÇÃO CADASTRAL]
        from [ReceitaFederal].[dbo].[EmpresasNacionaisPeriodo]
       ) t1
  WHERE [PORTE DA EMPRESA] < 3 AND [SITUAÇÃO CADASTRAL] > 2 --MANTEM APENAS MICROEMPRESAS desativadas
  GROUP BY ANOBAIXA, [CNAE FISCAL PRINCIPAL], [CEP]
