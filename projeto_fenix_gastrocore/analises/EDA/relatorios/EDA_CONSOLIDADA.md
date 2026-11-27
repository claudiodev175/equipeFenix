# GastroCore — Relatório Consolidado da EDA

## Escopo
Análise exploratória das bases disponíveis na camada Silver. Os arquivos de origem não foram alterados.

## Resumo das bases
| base                    | arquivo                                       |   registros |   colunas |   valores_ausentes |   linhas_duplicadas |
|:------------------------|:----------------------------------------------|------------:|----------:|-------------------:|--------------------:|
| consumo_cmv             | gastrocore_consumo_cmv_silver.csv             |          20 |        17 |                  0 |                   0 |
| desperdicio             | gastrocore_desperdicio_rdc216_silver.csv      |          30 |        16 |                  0 |                   0 |
| filiais                 | gastrocore_filiais_pe_silver.csv              |           5 |        11 |                  0 |                   0 |
| processamento_proteinas | gastrocore_processamento_proteinas_silver.csv |          18 |        17 |                  0 |                   0 |
| requisicoes_compras     | gastrocore_requisicoes_compras_silver.csv     |          18 |        13 |                  0 |                   0 |

**Total de registros analisados:** 91
**Total de colunas analisadas:** 74
**Total de valores ausentes:** 0
**Total de linhas integralmente duplicadas:** 0

## Relatórios individuais
- [EDA consumo_cmv](EDA_consumo_cmv.md)
- [EDA desperdicio](EDA_desperdicio.md)
- [EDA filiais](EDA_filiais.md)
- [EDA processamento_proteinas](EDA_processamento_proteinas.md)
- [EDA requisicoes_compras](EDA_requisicoes_compras.md)

## Ressalvas transversais
- Ausência de valores nulos ou duplicatas integrais não comprova validade semântica.
- As bases têm granularidades, períodos e unidades diferentes; não devem ser combinadas sem regras explícitas.
- A base de filiais contém cadastro de unidades e não deve ser interpretada como amostra operacional equivalente às demais.
- Correlações e associações não demonstram causalidade.
- Os dados e as regras devem ser confirmados pelo CESIC antes de decisões operacionais ou homologação.

## Limitações
- Resultados restritos aos arquivos Silver fornecidos.
- Não foram inferidos dados ausentes nem corrigidos valores de origem.
- Verificações específicas são testes aritméticos/indicativos, não substituem validação formal das regras de negócio.

## Status
Relatório exploratório gerado automaticamente. Requer revisão técnica e validação das regras pelo CESIC.