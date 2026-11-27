# Fenix GastroCore — Silver Pipeline V2 (Quality Controls)

## Objetivo

A V2 mantém a validação obrigatória SHA-256 da Bronze e as regras de limpeza da V1. Acrescenta controles complementares de consistência aritmética e indicadores derivados de qualidade, sem corrigir ou apagar valores de origem.

## Pré-requisitos

- Python 3.10 ou superior
- pandas
- Cinco CSVs Bronze
- `manifesto_integridade_bronze.csv`

Instalação:

```powershell
python -m pip install pandas
```

## Estrutura esperada

```text
projeto_fenix_gastrocore/
├── artefato_pipeline_ limpeza/
│   ├── silver_pipeline.py
│   └── README_execucao_silver_v2.md
└── Dados_projeto_fenix/
    ├── gastrocore_consumo_cmv.csv
    ├── gastrocore_desperdicio_rdc216.csv
    ├── gastrocore_filiais_pe.csv
    ├── gastrocore_processamento_proteinas.csv
    └── gastrocore_requisicoes_compras.csv
```

O manifesto deve estar em:

`Dados_projeto_fenix/data/quality_reports/manifesto_integridade_bronze.csv`

## Execução

A partir da raiz do projeto, no PowerShell:

```powershell
$script = Get-ChildItem -Path . -Recurse -Filter silver_pipeline.py |
    Where-Object { $_.FullName -like '*artefato_pipeline*' } |
    Select-Object -First 1 -ExpandProperty FullName

python $script `
  --input-dir ".\Dados_projeto_fenix" `
  --output-dir ".\Dados_projeto_fenix\data\silver"
```

O pipeline localiza automaticamente o manifesto no diretório padrão. Para informar outro caminho, use `--manifest "CAMINHO\manifesto.csv"`.

## Controles adicionados na V2

### Consumo CMV

- Quantidade prevista × custo unitário = CMV orçado (tolerância R$ 0,01).
- Quantidade real × custo unitário = CMV realizado (tolerância R$ 0,01).
- CMV realizado − CMV orçado = desvio em reais (tolerância R$ 0,01).
- Desvio em reais ÷ CMV orçado × 100 = desvio percentual (tolerância 0,01 ponto percentual).

São verificações aritméticas exploratórias baseadas nos campos e fórmulas já auditados; não substituem validação formal da regra de negócio pela CESIC.

### Desperdício RDC 216

- Cria `indicador_temperatura_zero`.
- Cria `indicador_temperatura_abaixo_60` somente para `Sobra Limpa (Nao Distribuida)`.
- Cria `status_validacao_temperatura`.
- Temperatura zero permanece zero e recebe `ZERO_PENDENTE_INTERPRETACAO`. Não é convertida em nulo nem excluída.
- Temperaturas abaixo de 60 °C em sobra limpa recebem alerta para revisão. O limite não é aplicado indiscriminadamente a todos os tipos de descarte.

A regra CESIC sobre temperatura 0,0 °C sem viagem continua pendente de confirmação, pois o CSV não possui campo que identifique viagem.

### Processamento de proteínas

- Mantém as validações PB ≥ PL e FC ≥ 1.
- Compara `perda_pct` com `limite_perda_pct`.
- Cria `comparacao_limite_perda` (ACIMA_DO_LIMITE, ABAIXO_DO_LIMITE, NO_LIMITE) e `diferenca_limite_perda_pp`.
- Preserva `status_perda` e todos os campos originais.

### Requisições de compras

- Mantém quantidade solicitada = entregue + pendente.
- Verifica quantidade solicitada × valor unitário estimado = valor total estimado (tolerância R$ 0,01).

## Regras preservadas da V1

- Validação SHA-256 obrigatória antes de qualquer transformação.
- Padronização conservadora de cabeçalhos e textos.
- Tipagem explícita de datas e números.
- Remoção somente de linhas integralmente duplicadas.
- Conflitos de chave, ausências e erros de conversão são reportados.
- Sem imputação automática e sem correção de valores suspeitos.
- Bronze nunca é sobrescrita.

## Saídas

- Cinco CSVs Silver em `data/silver`.
- `relatorio_quality_silver.md`.
- `relatorio_quality_silver.json`.

## Interpretação

Os controles complementares são verificações de consistência dos dados, não declarações automáticas de erro operacional. Ocorrências devem ser analisadas com o contexto e as regras oficiais. Os campos originais permanecem preservados; os indicadores derivados são adicionados para facilitar a revisão.
