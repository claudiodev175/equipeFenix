# DOSSIÊ TÉCNICO — SPRINT 1
## Projeto Fenix GastroCore
### Preparação e Qualidade dos Dados — Camadas Bronze e Silver

| Informação | Descrição |
|---|---|
| Projeto | Fenix GastroCore |
| Organização | CESIC Tecnologias |
| Etapa | Sprint 1 |
| Escopo | Engenharia e preparação dos dados |
| Camadas | Bronze e Silver |
| Data de referência | 27/11/2026 |
| Versão | 1.0 |

---

# 1. Objetivo

Este documento registra as atividades técnicas realizadas na Sprint 1 do projeto Fenix GastroCore, com foco na preservação da camada Bronze e na implementação do processo de transformação e validação da camada Silver.

O trabalho teve como objetivos:

- Preservar a integridade dos arquivos originais.
- Automatizar a higienização e padronização dos dados.
- Realizar conversões e validações de tipos.
- Identificar inconsistências e possíveis problemas de qualidade.
- Produzir arquivos Silver rastreáveis.
- Documentar decisões técnicas, evidências e limitações.

As atividades foram orientadas pelo documento CESIC Tecnologias — Dicionário de Dados v0.3.0 & Medallion — GastroCore ERP e pelos arquivos disponibilizados para o projeto.

# 2. Escopo e fontes de dados

Foram processados cinco arquivos CSV disponibilizados no conjunto de dados do projeto.

| Arquivo de origem | Registros |
|---|---:|
| gastrocore_consumo_cmv.csv | 20 |
| gastrocore_desperdicio_rdc216.csv | 30 |
| gastrocore_filiais_pe.csv | 5 |
| gastrocore_processamento_proteinas.csv | 18 |
| gastrocore_requisicoes_compras.csv | 18 |
| **Total** | **91** |

Os arquivos de processamento de proteínas e requisições de compras foram incluídos por terem sido disponibilizados junto ao projeto, embora não constem na relação dos três datasets sintéticos iniciais enumerados no documento CESIC v0.3.0.

# 3. Arquitetura de dados

A implementação segue o conceito de arquitetura Medallion.

## 3.1. Bronze — dados originais

A camada Bronze representa os arquivos recebidos da origem, preservados sem transformações.

Foi adotada a política de não sobrescrever nem modificar os arquivos originais.

## 3.2. Silver — dados tratados

A camada Silver recebe os dados após os procedimentos de limpeza, padronização, conversão e validação.

Foram produzidos cinco arquivos:

- `gastrocore_consumo_cmv_silver.csv`
- `gastrocore_desperdicio_rdc216_silver.csv`
- `gastrocore_filiais_pe_silver.csv`
- `gastrocore_processamento_proteinas_silver.csv`
- `gastrocore_requisicoes_compras_silver.csv`

## 3.3. Organização dos artefatos

Os principais diretórios utilizados são:

```text
projeto_fenix_gastrocore/
│
├── artefato_pipeline_ limpeza/
│   ├── silver_pipeline.py
│   ├── silver_pipeline_v1_backup.py
│   ├── README_execucao_silver_v2.md
│   └── requirements_silver.txt
│
└── Dados_projeto_fenix/
    ├── gastrocore_schema.json
    ├── schema.sql
    └── data/
        ├── silver/
        └── quality_reports/
```

# 4. Integridade da camada Bronze

## 4.1. Método

Foi implementada uma auditoria utilizando o algoritmo SHA-256 para comparar os cinco arquivos CSV extraídos com seus respectivos arquivos existentes no pacote ZIP de referência.

Foram gerados:

- `relatorio_integridade_bronze_sha256.csv`
- `manifesto_integridade_bronze.csv`

O manifesto passou a ser uma etapa obrigatória do pipeline Silver.

Antes de executar qualquer transformação, o script verifica:

1. Existência do manifesto.
2. Presença dos cinco arquivos esperados.
3. Situação registrada como `INTEGRO`.
4. Correspondência entre os hashes calculados e os hashes de referência.
5. Identificação do pacote ZIP de origem.

Caso seja detectada divergência, o processamento é interrompido.

## 4.2. Resultado

| Indicador | Resultado |
|---|---:|
| Arquivos auditados | 5 |
| Arquivos íntegros | 5 |
| Arquivos divergentes | 0 |
| Arquivos não conformes | 0 |

**Resultado:** os cinco arquivos locais apresentaram correspondência byte a byte com os arquivos de referência do pacote ZIP auditado.

Hash SHA-256 do pacote ZIP registrado no manifesto:

```text
B2F97C0BA4B8B59D84BE2C414DC88D9C46E9053061CB08A5021088EC126D3484
```

A comprovação refere-se à correspondência com o pacote de referência utilizado na auditoria. Não constitui prova histórica de que os arquivos jamais tenham sido modificados anteriormente, nem abrange as 13 tabelas operacionais do banco PostgreSQL.

# 5. Pipeline de transformação Silver

Foi desenvolvido um pipeline automatizado em Python, utilizando Pandas.

## 5.1. Procedimentos implementados

| Procedimento | Tratamento |
|---|---|
| Integridade | Verificação SHA-256 antes do processamento |
| Cabeçalhos | Padronização para letras minúsculas e underscore |
| Textos | Remoção de espaços excedentes |
| Datas | Conversão explícita dos campos de data |
| Numéricos | Conversão explícita dos campos numéricos |
| Inteiros | Conversão dos campos definidos como inteiros |
| Duplicidades | Remoção somente de linhas integralmente idênticas |
| Chaves | Verificação de duplicidades nos identificadores avaliados |
| Regras | Aplicação dos controles documentados e verificações complementares |
| Indicadores | Criação de colunas derivadas para análise da qualidade |

## 5.2. Política de transformação

Foram adotados os seguintes princípios:

- Não modificar a camada Bronze.
- Não imputar valores ausentes.
- Não corrigir automaticamente valores suspeitos.
- Não excluir registros apenas por apresentarem alertas.
- Não converter valores zero em nulos sem confirmação semântica.
- Preservar os campos originais de status.
- Documentar regras pendentes de confirmação.

A política prioriza rastreabilidade e preservação da informação original.

# 6. Resultados das validações por dataset

## 6.1. Consumo e CMV

**Arquivo:** `gastrocore_consumo_cmv_silver.csv`

Registros avaliados: 20.

Foram verificadas as seguintes consistências aritméticas:

- Quantidade prevista × custo unitário = CMV orçado.
- Quantidade real × custo unitário = CMV realizado.
- Compatibilidade entre desvio em reais e diferença dos valores.
- Compatibilidade do percentual de desvio.
- Consistência dos fatores de conversão.

**Resultado:** nenhuma inconsistência identificada nas verificações realizadas.

O relatório V2 não identificou erros de conversão, ausências ou conflitos nas chaves avaliadas.

## 6.2. Desperdício e RDC 216

**Arquivo:** `gastrocore_desperdicio_rdc216_silver.csv`

Registros avaliados: 30.

A auditoria identificou:

- 13 registros com temperatura igual a 0,0 °C.
- 2 registros de sobra limpa com temperatura inferior a 60 °C.
- Os demais registros de sobra limpa apresentaram temperaturas iguais ou superiores a 60 °C.
- Os 13 registros com temperatura zero estão associados ao tipo de descarte `Resto Ingesta (Descarte Prato)`.

Foram adicionadas três colunas derivadas:

- `indicador_temperatura_zero`
- `indicador_temperatura_abaixo_60`
- `status_validacao_temperatura`

A presença das três colunas foi confirmada por inspeção estrutural do CSV Silver.

### Tratamento dos valores zero

Os 13 registros foram preservados.

Não foram convertidos para valores nulos nem interpretados automaticamente como ausência de aferição.

O documento CESIC v0.3.0 menciona o filtro de temperatura 0,0 °C sem viagem. Entretanto, os CSVs analisados não apresentam um campo que permita identificar diretamente a existência ou ausência de viagem.

Assim, não foi possível confirmar a aplicação integral dessa regra.

### Registros de sobra limpa abaixo de 60 °C

Foram identificados dois casos:

| ID | Temperatura | Observação |
|---|---:|---|
| 4 | 58,4 °C | Queda de temperatura no transporte Hot Box |
| 17 | 56,9 °C | Atraso de 40 minutos em trânsito na rodovia PE-060 |

Os casos foram mantidos como alertas operacionais, sem alteração dos valores originais ou do status sanitário.

**Pendência:** a distribuição dos valores da coluna `status_validacao_temperatura` ainda precisa ser conferida por agrupamento no CSV Silver.

## 6.3. Cadastro de filiais

**Arquivo:** `gastrocore_filiais_pe_silver.csv`

Registros avaliados: 5.

Foram realizadas verificações de:

- Conversão de campos.
- Padronização de cabeçalhos.
- Campos vazios.
- Identificadores de filiais.
- Relacionamentos com os datasets de CMV e desperdício.

Os relacionamentos entre `id_filial` dos arquivos de CMV e desperdício e o cadastro de filiais PE foram avaliados sem identificação de chaves órfãs.

Foi identificada divergência de acentuação no nome de uma filial entre datasets. Os identificadores foram preservados como referência principal, sem correção automática do nome.

## 6.4. Processamento de proteínas

**Arquivo:** `gastrocore_processamento_proteinas_silver.csv`

Registros avaliados: 18.

Foram realizadas verificações de:

- Peso bruto maior ou igual ao peso limpo.
- Consistência entre peso pós-descongelamento, aparas, rejeitos e peso limpo.
- Compatibilidade entre perda total e diferença entre peso bruto e peso limpo.
- Compatibilidade do percentual de perda.
- Fator de conversão maior ou igual a 1.
- Comparação do percentual de perda com o limite informado em cada registro.

Foram adicionadas duas colunas derivadas:

- `comparacao_limite_perda`
- `diferenca_limite_perda_pp`

### Resultado da comparação dos limites

| Classificação | Registros | Percentual |
|---|---:|---:|
| Acima do limite | 8 | 44,4% |
| Abaixo do limite | 8 | 44,4% |
| No limite | 2 | 11,1% |
| **Total** | **18** | **100%** |

A distribuição dos indicadores materializados no CSV Silver foi conferida por agrupamento e corresponde à auditoria matemática anterior.

Os status originais foram preservados. A classificação derivada não substitui o campo `status_perda`.

**Interpretação:** os oito registros acima do limite representam alertas para análise operacional. Não devem ser tratados automaticamente como erros de dados.

As fórmulas utilizadas nesta auditoria são verificações aritméticas complementares, baseadas nos campos disponíveis. Sua adoção como regra oficial de negócio depende de confirmação, quando aplicável.

## 6.5. Requisições de compras

**Arquivo:** `gastrocore_requisicoes_compras_silver.csv`

Registros avaliados: 18.

Foram verificadas:

- Quantidade solicitada = quantidade entregue + quantidade pendente.
- Valor total = quantidade solicitada × valor unitário estimado.
- Conversão dos campos numéricos.
- Datas.
- Campos vazios.

**Resultado:** nenhuma inconsistência aritmética identificada nas verificações realizadas.

### Unidades de medida encontradas

| Unidade | Ocorrências |
|---|---:|
| KG | 14 |
| UNI | 2 |
| UND | 1 |
| GL | 1 |

A equivalência semântica das unidades ainda depende de confirmação.

Em particular, não foi atribuída interpretação definitiva à unidade `GL`.

# 7. Auditorias transversais

## 7.1. Campos vazios

Não foram identificados campos vazios ou compostos somente por espaços nos 91 registros dos cinco arquivos Silver.

O teste realizado não comprova a ausência de marcadores textuais como `NULL` ou `N/A`.

## 7.2. Datas

Todos os campos de data avaliados foram interpretados corretamente.

| Dataset | Campo | Registros válidos | Inválidos |
|---|---|---:|---:|
| CMV | data_competencia | 20 | 0 |
| Desperdício | data_registro | 30 | 0 |
| Processamento | data_processamento | 18 | 0 |
| Compras | data_solicitacao | 18 | 0 |

Períodos identificados:

- CMV e desperdício: 01/03/2026 a 04/03/2026.
- Compras: 02/11/2026 a 13/11/2026.
- Processamento: 02/11/2026 a 14/11/2026.

A diferença entre os períodos foi documentada, sem alteração artificial das datas.

## 7.3. Campos numéricos

Foram testados 32 campos numéricos nos cinco datasets.

Resultado:

- Nenhum valor inválido de conversão identificado.
- Todos os campos testados foram interpretáveis numericamente.

A conversão bem-sucedida não comprova, isoladamente, que todos os valores estejam dentro dos limites semânticos esperados.

## 7.4. Integridade referencial

Foram avaliados os relacionamentos entre os identificadores de filiais nos datasets de CMV e desperdício e o cadastro de filiais PE, sem chaves órfãs nesses relacionamentos.

Também foi identificado que os códigos `IND-01`, `HOSP-02` e `ESC-03`, utilizados nos datasets de processamento e compras, correspondem às unidades presentes no seed da tabela `kitchen_units`.

Esses códigos pertencem a um domínio diferente dos identificadores de filiais PE.

Por esse motivo, os domínios não foram cruzados como se representassem a mesma chave.

A integridade referencial completa do modelo PostgreSQL não foi comprovada nesta etapa.

# 8. Matriz de conformidade CESIC v0.3.0

| Código | Requisito | Situação |
|---|---|---|
| C01 | Preservação da Bronze | Conforme para os cinco CSVs auditados |
| C02 | Higienização dos dados | Parcialmente verificado |
| C03 | Padronização de datas | Conforme nos campos testados |
| C04 | Padronização de unidades | Parcial; equivalências pendentes |
| C05 | Fator de conversão ≥ 1 | Conforme nos campos testados |
| C06 | Peso bruto ≥ peso limpo | Conforme nos registros testados |
| C07 | Zero chaves órfãs | Parcial; relacionamentos avaliados sem órfãos |
| C08 | Temperatura 0,0 °C sem viagem | Pendente de confirmação semântica |
| C09 | Detecção de lotes vencidos | Não verificável nos CSVs analisados |
| C10 | Higienização e validação DA-1 | Parcialmente verificado |

## 8.1. Pendências para confirmação da CESIC

1. Confirmar o significado operacional de temperatura igual a 0,0 °C e a condição de aplicação do filtro sem viagem.
2. Confirmar o domínio oficial das unidades de medida, especialmente `UNI`, `UND` e `GL`.
3. Confirmar os domínios oficiais dos campos categóricos, como turno e status sanitário.
4. Confirmar as regras formais de cálculo utilizadas nas verificações aritméticas complementares.
5. Disponibilizar os dados de lote, validade e demais informações necessárias à detecção de lotes vencidos.
6. Definir o escopo de validação referencial entre os CSVs e as 13 tabelas do PostgreSQL.

# 9. Evidências e artefatos produzidos

| Artefato | Finalidade |
|---|---|
| `Dados_projeto_fenix.zip` | Pacote original de dados |
| `manifesto_integridade_bronze.csv` | Registro dos hashes de referência |
| `relatorio_integridade_bronze_sha256.csv` | Resultado da auditoria de integridade |
| `silver_pipeline.py` | Pipeline de processamento V2 |
| `silver_pipeline_v1_backup.py` | Backup da versão anterior |
| `README_execucao_silver_v2.md` | Instruções de execução |
| Cinco arquivos Silver | Dados transformados |
| `relatorio_quality_silver.md` | Relatório legível de qualidade |
| `relatorio_quality_silver.json` | Relatório estruturado de qualidade |

A execução real do pipeline apresentou:

```text
Integridade Bronze aprovada: 5/5 arquivos íntegros.
Arquivos Silver gerados: 5/5
```

O relatório V2 registrou:

- Cinco arquivos processados.
- 91 registros preservados.
- Nenhuma duplicata integral removida.
- Nenhum arquivo ausente.
- Nenhum erro de conversão identificado nos controles reportados.
- Indicadores derivados de temperatura e perda presentes nos respectivos arquivos Silver.

Essas evidências comprovam a execução documentada e os resultados dos controles realizados. Não substituem testes de integração com o banco PostgreSQL.

# 10. Decisões técnicas

| Decisão | Justificativa |
|---|---|
| Preservar a Bronze | Garantir rastreabilidade e possibilidade de reprodução |
| Utilizar SHA-256 | Verificar correspondência com o pacote de referência |
| Bloquear o pipeline em caso de divergência | Evitar transformar arquivos não aprovados |
| Remover somente duplicatas integrais | Evitar exclusão indevida de registros distintos |
| Não imputar dados ausentes | Evitar introduzir informações não fornecidas pela origem |
| Preservar valores de temperatura zero | Evitar interpretação semântica indevida |
| Criar indicadores derivados | Permitir análise sem alterar campos originais |
| Preservar status originais | Separar informação recebida de classificação complementar |
| Não unificar códigos de unidades e filiais | Evitar relacionamentos incorretos entre domínios distintos |

# 11. Limitações técnicas e semânticas

Apesar dos resultados positivos, algumas limitações precisam ser explicitadas.

**Limitações dos dados:**

- O conjunto contém 91 registros.
- Os cinco CSVs não representam necessariamente a totalidade das 13 tabelas operacionais descritas no esquema PostgreSQL.
- Não há campos suficientes nos CSVs analisados para validar a regra completa de lotes vencidos.
- Não existe informação explícita de viagem que permita confirmar a regra de temperatura zero sem viagem.

**Limitações das validações:**

- Os testes numéricos não comprovam, por si só, a validade semântica de todas as unidades.
- As fórmulas aritméticas complementares dependem de confirmação formal quando forem adotadas como regras oficiais.
- A integridade referencial foi verificada somente nos relacionamentos explicitamente avaliados.
- A comparação com limites de perda é descritiva e não constitui avaliação conclusiva de desempenho operacional.
- A distribuição do campo `status_validacao_temperatura` ainda precisa de conferência específica.

# 12. Resultado consolidado da Sprint 1

| Indicador | Resultado |
|---|---:|
| Arquivos de origem auditados | 5 |
| Arquivos Silver produzidos | 5 |
| Registros de origem | 91 |
| Registros preservados | 91 |
| Divergências SHA-256 | 0 |
| Duplicatas integrais removidas | 0 |
| Campos numéricos testados | 32 |
| Campos de data testados | 4 |
| Indicadores derivados de temperatura | 3 |
| Indicadores derivados de perda | 2 |
| Registros de processamento de proteínas | 18 |
| Registros acima do limite de perda | 8 |
| Registros de desperdício com temperatura zero | 13 |

# 13. Conclusão técnica

A Sprint 1 estabeleceu um processo automatizado e rastreável de preparação dos cinco datasets CSV do Fenix GastroCore.

A camada Bronze foi preservada e auditada por SHA-256, enquanto a camada Silver foi produzida por meio de um pipeline Python com controles de integridade, padronização, conversão e validação.

Os 91 registros foram preservados, sem remoção de duplicatas integrais. As verificações realizadas não identificaram erros de conversão nos controles reportados, e os indicadores derivados foram materializados nos arquivos correspondentes.

O resultado representa uma entrega técnica consistente da etapa de preparação dos dados, com pendências semânticas e de conformidade documentadas.

A camada Silver está tecnicamente preparada para avançar para as próximas atividades, desde que as limitações identificadas sejam consideradas e as regras pendentes sejam confirmadas antes de sua utilização como regras definitivas de negócio.

# 14. Encaminhamentos

1. Registrar formalmente as dúvidas semânticas para a CESIC.
2. Confirmar a distribuição do indicador `status_validacao_temperatura`.
3. Consolidar a versão de referência do pipeline e dos relatórios.
4. Validar a integração entre os arquivos Silver e o esquema PostgreSQL.
5. Planejar a modelagem da camada Gold, respeitando os domínios e relacionamentos confirmados.

---

**Sprint 1 — Bronze e Silver**

**Status:** execução técnica realizada para os cinco CSVs disponibilizados, com evidências registradas e pendências de conformidade e confirmação de regras de negócio identificadas.