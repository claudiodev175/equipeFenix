# Fenix GastroCore — Relatório de Qualidade Silver

- Gerado em (UTC): 2026-11-27T20:47:24.164306+00:00
- Arquivos processados: 5/5
- Arquivos ausentes: Nenhum

## Integridade da camada Bronze

- Manifesto: `manifesto_integridade_bronze.csv`
- Método: SHA-256
- Arquivos verificados: 5/5
- Resultado: **APROVADO**
- SHA-256 do pacote ZIP registrado: `B2F97C0BA4B8B59D84BE2C414DC88D9C46E9053061CB08A5021088EC126D3484`

| Arquivo | Status | SHA-256 atual |
|---|---|---|
| gastrocore_consumo_cmv.csv | INTEGRO | `EBF9AF445B3158E1D1092323FD3DFEE3F37D6104092911504CAC4EE738B276A2` |
| gastrocore_desperdicio_rdc216.csv | INTEGRO | `918D77F36A87A894F6BC5C9B92E9A157D4FA2B1A2752A2519BB214E922E0C92E` |
| gastrocore_filiais_pe.csv | INTEGRO | `523FFBCD04B74BB2825345664DD9F59726D35F8DE670EF10C9AFBC25DE409BA5` |
| gastrocore_processamento_proteinas.csv | INTEGRO | `2BCBFED1E1AC861AD97A932A9183C962AF0CF1289A38FCE0E0F8E7C0029C21DA` |
| gastrocore_requisicoes_compras.csv | INTEGRO | `ADEF166387E0179A043D85623EF93D323C9DDE97D5BAE8DB39A0B21CB5A458A7` |

## Resultados por arquivo

| Arquivo | Linhas Bronze | Linhas Silver | Duplicatas exatas removidas |
|---|---:|---:|---:|
| gastrocore_consumo_cmv.csv | 20 | 20 | 0 |
| gastrocore_desperdicio_rdc216.csv | 30 | 30 | 0 |
| gastrocore_filiais_pe.csv | 5 | 5 | 0 |
| gastrocore_processamento_proteinas.csv | 18 | 18 | 0 |
| gastrocore_requisicoes_compras.csv | 18 | 18 | 0 |

## gastrocore_consumo_cmv.csv

- Erros de conversão: `Nenhum`
- Ausências: `Nenhuma`
- Conflitos de chave mantidos: `Nenhum`
- Regras: `{'fator_correcao_real_GE_1': {'invalid_rows': 0, 'rule': 'fator_correcao_real >= 1'}, 'fator_correcao_teorico_GE_1': {'invalid_rows': 0, 'rule': 'fator_correcao_teorico >= 1'}, 'CMV_ORCADO_ARITMETICAMENTE_COMPATIVEL': {'invalid_rows': 0, 'rule': 'qtd_prevista_kg * custo_unitario_kg = cmv_orcado_reais (tolerância R$ 0,01)'}, 'CMV_REALIZADO_ARITMETICAMENTE_COMPATIVEL': {'invalid_rows': 0, 'rule': 'qtd_real_kg * custo_unitario_kg = cmv_realizado_reais (tolerância R$ 0,01)'}, 'DESVIO_CMV_ARITMETICAMENTE_COMPATIVEL': {'invalid_rows': 0, 'rule': 'cmv_realizado_reais - cmv_orcado_reais = desvio_cmv_reais (tolerância R$ 0,01)'}, 'PERCENTUAL_DESVIO_CMV_COMPATIVEL': {'invalid_rows': 0, 'rule': 'desvio_cmv_reais / cmv_orcado_reais * 100 = desvio_cmv_percentual (tolerância 0,01 ponto percentual)'}}`

## gastrocore_desperdicio_rdc216.csv

- Erros de conversão: `Nenhum`
- Ausências: `Nenhuma`
- Conflitos de chave mantidos: `Nenhum`
- Regras: `{'TEMPERATURA_ZERO_PENDENTE_INTERPRETACAO': {'ocorrencias': 13, 'regra': 'temperatura igual a zero é sinalizada; valor original preservado; não inferir ausência de aferição'}, 'SOBRA_LIMPA_ABAIXO_60C': {'ocorrencias': 2, 'regra': 'temperatura abaixo de 60 °C em Sobra Limpa (Nao Distribuida); indicador exploratório para revisão'}}`

## gastrocore_filiais_pe.csv

- Erros de conversão: `Nenhum`
- Ausências: `Nenhuma`
- Conflitos de chave mantidos: `Nenhum`
- Regras: `Nenhuma regra específica aplicável`

## gastrocore_processamento_proteinas.csv

- Erros de conversão: `Nenhum`
- Ausências: `Nenhuma`
- Conflitos de chave mantidos: `Nenhum`
- Regras: `{'PB_GE_PL': {'invalid_rows': 0, 'rule': 'peso_bruto_kg >= peso_limpo_kg'}, 'fator_correcao_real_GE_1': {'invalid_rows': 0, 'rule': 'fator_correcao_real >= 1'}, 'FC_REAL_COMPATIVEL_COM_PB_PL': {'invalid_rows': 0, 'rule': 'fator_correcao_real aproximadamente igual a peso_bruto_kg / peso_limpo_kg (tolerância 0,02)'}, 'PERDA_PCT_COMPARADA_AO_LIMITE': {'acima_do_limite': 8, 'abaixo_do_limite': 8, 'no_limite': 2, 'regra': 'comparação descritiva de perda_pct com limite_perda_pct; não altera status_perda original'}}`

## gastrocore_requisicoes_compras.csv

- Erros de conversão: `Nenhum`
- Ausências: `Nenhuma`
- Conflitos de chave mantidos: `Nenhum`
- Regras: `{'QTD_SOLICITADA_EQ_ENTREGUE_MAIS_PENDENTE': {'invalid_rows': 0, 'rule': 'qtd_solicitada = qtd_entregue + qtd_pendente'}, 'VALOR_TOTAL_COMPRA_COMPATIVEL': {'invalid_rows': 0, 'rule': 'qtd_solicitada * valor_unit_estimado = valor_total_estimado (tolerância R$ 0,01)'}}`

## Política de tratamento

- A validação SHA-256 do manifesto é obrigatória e antecede qualquer transformação.
- Os arquivos Bronze não são sobrescritos.
- Textos recebem remoção de espaços periféricos e repetidos; acentos e rótulos são preservados.
- Datas e números recebem tipagem explícita.
- Somente linhas integralmente duplicadas são removidas automaticamente.
- Conflitos de chave, valores ausentes e violações de regra são reportados para revisão.
- Nenhum valor ausente é imputado e nenhum valor suspeito é corrigido sem regra aprovada.

## Limitações e pontos de atenção

- Ruptura de estoque e lote vencido dependem de fonte com saldo mínimo, estoque atual e validade; não são inferidos dos cinco CSVs atuais.
- PB >= PL e FC >= 1 são avaliados no arquivo de processamento de proteínas e nos campos de FC disponíveis.
- A relação solicitada = entregue + pendente e o valor total estimado de compras são verificados aritmeticamente.
- As fórmulas de CMV são verificações aritméticas complementares, com tolerância de R$ 0,01 e 0,01 ponto percentual.
- A comparação de perda com limite é descritiva; status_perda original não é alterado.
- Temperatura zero é sinalizada como pendente de interpretação; não é convertida em nulo.
- O alerta abaixo de 60 °C é aplicado apenas a Sobra Limpa (Nao Distribuida), não a todos os tipos de descarte.