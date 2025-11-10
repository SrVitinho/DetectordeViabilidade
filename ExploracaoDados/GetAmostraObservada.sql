drop table if exists ReceitaFederal..EmpresasNacionaisPeriodoAmostra;

select *
into ReceitaFederal..EmpresasNacionaisPeriodoAmostra
from ReceitaFederal..EmpresasNacionaisPeriodo
where [CNPJ BÁSICO]%100 in (87, 88, 89, 90, 90)