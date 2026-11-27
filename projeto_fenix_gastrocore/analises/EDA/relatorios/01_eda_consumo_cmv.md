# EDA 01 — Consumo CMV
## Fenix GastroCore | Sprint 1

### 1. Objetivo e fonte
Analisar exploratoriamente `gastrocore_consumo_cmv_silver.csv`, preservando os dados de origem. A análise contempla estrutura, estatística descritiva, distribuição, padrões, relações entre variáveis, implicações para a camada Gold e limitações.

**Fonte:** camada Silver entregue no pacote `silver.zip`. **Escopo:** 20 registros e 17 colunas.

### 2. Auditoria estrutural
- Registros: 20; colunas: 17
- Valores ausentes: 0
- Linhas integralmente duplicadas: 0
- IDs `id_consumo` duplicados: 0
- Filiais: 4; datas distintas: 4

A ausência de nulos e duplicatas integrais não comprova, isoladamente, a validade semântica dos campos.

### 3. Indicadores consolidados
| Indicador | Resultado |
|---|---:|
| Quantidade prevista | 4,080.00 kg |
| Quantidade realizada | 4,400.00 kg |
| Diferença de quantidade | 320.00 kg |
| CMV orçado | R$ 102,025.50 |
| CMV realizado | R$ 109,563.35 |
| Desvio financeiro | R$ 7,537.85 |
| Desvio percentual ponderado | 7.39% |
| Média simples dos percentuais por registro | 8.14% |

**Nota metodológica:** percentual ponderado = desvio financeiro total / CMV orçado total. A média simples dos percentuais por registro responde a outra pergunta e não deve ser confundida com o indicador agregado.

### 4. Distribuição e comportamento
- Quantidade realizada supera a prevista em 320.00 kg (7.84%).
- Classificação ABC (contagem de registros): {'Curva A': 12, 'Curva B': 5, 'Curva C': 3} — não representa participação financeira.
- 4 filiais e 8 categorias na amostra.

### 5. Desvio por categoria
| categoria_insumo        |   registros |   desvio_financeiro |   desvio_percentual_medio |
|:------------------------|------------:|--------------------:|--------------------------:|
| Proteina Bovina         |           5 |             4870.75 |                      9.28 |
| Hortifruti              |           6 |              708.30 |                     13.26 |
| Proteina Suina          |           2 |              648.00 |                      5.59 |
| Proteina Ave            |           2 |              485.10 |                      4.11 |
| Proteina Peixe          |           1 |              456.00 |                      6.67 |
| Proteina Caprina/Bovina |           1 |              252.00 |                      3.16 |
| Laticinios              |           1 |               61.50 |                      1.67 |
| Graos e Cereais         |           2 |               56.20 |                      2.97 |

Proteína Bovina soma R$ 4,870.75, equivalente a 64.6% do desvio financeiro total. Hortifruti apresenta a maior média simples de desvio percentual entre categorias (13.26%), mas não o maior impacto financeiro absoluto.

### 6. Desvio por filial
| nome_filial                     |   registros |   cmv_orcado |   cmv_realizado |   desvio_financeiro |   desvio_percentual_ponderado |
|:--------------------------------|------------:|-------------:|----------------:|--------------------:|------------------------------:|
| Cozinha Central Recife Antigo   |          11 |     62449.50 |        67189.55 |             4740.05 |                          7.59 |
| Cozinha Satelite Complexo Suape |           4 |     22845.00 |        24735.00 |             1890.00 |                          8.27 |
| Unidade Polo Caruaru            |           3 |      9436.00 |         9874.80 |              438.80 |                          4.65 |
| Unidade Vale Petrolina          |           2 |      7295.00 |         7764.00 |              469.00 |                          6.43 |

A maior contribuição absoluta ao desvio é da Cozinha Central Recife Antigo. A maior taxa ponderada entre as filiais é da Cozinha Satélite Complexo Suape. A comparação é descritiva, pois os volumes de registros são desiguais.

### 7. Relações entre variáveis
A matriz de correlação está disponível no notebook. Correlações envolvendo CMV, desvios e quantidades devem ser interpretadas com cautela: algumas variáveis são calculadas a partir das mesmas grandezas. Não se infere causalidade.

### 8. Achados, hipóteses e limitações
**Achados sustentados:** (1) desvio financeiro agregado de R$ 7,537.85 (7.39% do CMV orçado); (2) Proteína Bovina representa 64.6% do desvio; (3) quantidade realizada agregada supera a prevista em 7.84%.

**Hipóteses:** variações de rendimento, especificação ou qualidade do insumo podem contribuir para os desvios; os registros, isoladamente, não provam essas causas.

**Limitações:** amostra de 20 registros; apenas 4 datas; distribuição desigual por filial e categoria; regras oficiais da Curva ABC e dos fatores de correção dependem de homologação do CESIC; não há base suficiente para afirmar sazonalidade, tendência ou causalidade.

### 9. Recomendações para Gold
Considerar uma tabela fato de consumo/CMV relacionada a dimensões de tempo, filial e insumo. Confirmar chaves e semântica antes da implementação. Indicadores sugeridos: CMV orçado/realizado, desvio financeiro, percentual ponderado, variação de quantidade e fator de correção teórico versus real.

### 10. Reprodutibilidade
O notebook `01_eda_consumo_cmv.ipynb` contém leitura, auditoria, cálculos, agrupamentos, correlações e gráficos. Execute-o no mesmo diretório do CSV incluído neste pacote.

**Status:** EDA individual preliminar documentada. Homologação das regras de negócio permanece pendente.
