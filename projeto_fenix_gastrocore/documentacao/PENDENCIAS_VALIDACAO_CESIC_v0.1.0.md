# PENDÃŠNCIAS DE VALIDAÃ‡ÃƒO CESIC
**Projeto:** Fenix GastroCore
**Camada:** Silver
**VersÃ£o:** 0.1.0
**Status:** Aguardando esclarecimentos e validaÃ§Ã£o da CESIC

## 1. Objetivo

Registrar as questÃµes tÃ©cnicas e operacionais identificadas durante a preparaÃ§Ã£o e validaÃ§Ã£o dos dados da camada Silver, cuja resoluÃ§Ã£o depende de esclarecimento ou confirmaÃ§Ã£o da CESIC.

As respostas deverÃ£o orientar a definiÃ§Ã£o das regras de negÃ³cio, a evoluÃ§Ã£o da pipeline e a validaÃ§Ã£o dos dados.

## 2. QuestÃµes para validaÃ§Ã£o

### P01 â€” Temperatura igual a zero

**Contexto:** Foram identificados 13 registros com temperatura igual a zero, todos classificados como Resto Ingesta.

**QuestÃ£o para CESIC:** O valor 0,0Â°C representa uma mediÃ§Ã£o efetiva, ausÃªncia de mediÃ§Ã£o, equipamento sem registro ou outra condiÃ§Ã£o operacional?

**Impacto tÃ©cnico:** DefiniÃ§Ã£o do tratamento correto do valor zero e do indicador de qualidade correspondente.

**Status:** Pendente.

### P02 â€” Regra de temperatura e informaÃ§Ã£o de viagem

**Contexto:** A anÃ¡lise anterior identificou uma regra de validaÃ§Ã£o relacionada Ã  temperatura e Ã  condiÃ§Ã£o de viagem. O conjunto de dados disponÃ­vel nÃ£o apresenta um campo especÃ­fico que permita verificar essa condiÃ§Ã£o.

**QuestÃ£o para CESIC:** Qual Ã© a definiÃ§Ã£o oficial da regra? Qual informaÃ§Ã£o operacional deve ser utilizada para identificar a condiÃ§Ã£o de viagem?

**Impacto tÃ©cnico:** Necessidade de identificar ou incorporar o campo de origem adequado antes de automatizar a validaÃ§Ã£o.

**Status:** Pendente.

### P03 â€” Unidades de medida nas requisiÃ§Ãµes de compras

**Contexto:** Foram identificadas as seguintes unidades:
- KG: 14 registros;
- UNI: 2 registros;
- UND: 1 registro;
- GL: 1 registro.

**QuestÃ£o para CESIC:** UNI e UND representam a mesma unidade? O que significa GL neste contexto? Existem regras oficiais de conversÃ£o?

**Impacto tÃ©cnico:** ConstruÃ§Ã£o de um dicionÃ¡rio de unidades e prevenÃ§Ã£o de comparaÃ§Ãµes ou agregaÃ§Ãµes incorretas.

**Status:** Pendente.

### P04 â€” CÃ³digos de unidades operacionais

**Contexto:** Foram identificados cÃ³digos como IND-01, HOSP-02 e ESC-03, alÃ©m dos cÃ³digos de filiais no padrÃ£o FIL.

**QuestÃ£o para CESIC:** Qual Ã© o significado e a finalidade de cada domÃ­nio de cÃ³digos? Existe uma tabela oficial de correspondÃªncia entre unidades operacionais e filiais?

**Impacto tÃ©cnico:** DefiniÃ§Ã£o correta das dimensÃµes e dos relacionamentos entre datasets.

**Status:** Pendente.

### P05 â€” FÃ³rmulas oficiais do processamento de proteÃ­nas

**Contexto:** A anÃ¡lise contempla peso bruto, peso limpo, peso pÃ³s-descongelamento, aparas, rejeitos, fator de correÃ§Ã£o e percentual de perda.

**QuestÃ£o para CESIC:** Quais sÃ£o as fÃ³rmulas oficiais para:
1. Peso limpo;
2. Perda total;
3. Percentual de perda;
4. Fator de correÃ§Ã£o;
5. ComparaÃ§Ã£o com o limite de perda?

A CESIC tambÃ©m deverÃ¡ informar se existem fÃ³rmulas especÃ­ficas por tipo de proteÃ­na ou processo.

**Impacto tÃ©cnico:** ImplementaÃ§Ã£o de validaÃ§Ãµes automatizadas com critÃ©rios oficiais, evitando pressupostos nÃ£o homologados.

**Status:** Pendente.

### P06 â€” Lotes e validade dos produtos

**Contexto:** Os CSVs analisados nÃ£o apresentam campos suficientes para verificar lote, data de validade e situaÃ§Ã£o de vencimento.

**QuestÃ£o para CESIC:** Esses dados estÃ£o disponÃ­veis em outra fonte? Qual sistema ou tabela contÃ©m as informaÃ§Ãµes de lote, fabricaÃ§Ã£o e validade?

**Impacto tÃ©cnico:** IdentificaÃ§Ã£o da fonte de dados necessÃ¡ria para implementar controles de validade.

**Status:** NÃ£o verificÃ¡vel na base atual.

### P07 â€” DefiniÃ§Ã£o da regra DA-1

**Contexto:** O critÃ©rio DA-1 foi identificado como parcialmente atendido, mas sua definiÃ§Ã£o operacional precisa ser confirmada.

**QuestÃ£o para CESIC:** Qual Ã© a definiÃ§Ã£o oficial de DA-1, quais campos devem ser considerados e quais condiÃ§Ãµes caracterizam conformidade ou nÃ£o conformidade?

**Impacto tÃ©cnico:** FormalizaÃ§Ã£o da regra e implementaÃ§Ã£o de validaÃ§Ãµes reproduzÃ­veis.

**Status:** Pendente.

## 3. Registro das respostas

| ID | QuestÃ£o | Resposta da CESIC | ResponsÃ¡vel | Data | Status |
|---|---|---|---|---|---|
| P01 | InterpretaÃ§Ã£o da temperatura zero | A preencher | A definir | A definir | Pendente |
| P02 | Regra de temperatura e viagem | A preencher | A definir | A definir | Pendente |
| P03 | EquivalÃªncia de unidades | A preencher | A definir | A definir | Pendente |
| P04 | DomÃ­nios de cÃ³digos operacionais | A preencher | A definir | A definir | Pendente |
| P05 | FÃ³rmulas de processamento | A preencher | A definir | A definir | Pendente |
| P06 | Fonte de lotes e validade | A preencher | A definir | A definir | Pendente |
| P07 | DefiniÃ§Ã£o da regra DA-1 | A preencher | A definir | A definir | Pendente |

## 4. CritÃ©rio para encerramento das pendÃªncias

Uma pendÃªncia somente deverÃ¡ ser considerada resolvida quando:
1. A CESIC fornecer a definiÃ§Ã£o ou documentaÃ§Ã£o oficial, quando aplicÃ¡vel.
2. A regra estiver registrada no dicionÃ¡rio de dados ou documento de regras de negÃ³cio.
3. A implementaÃ§Ã£o tÃ©cnica estiver documentada, quando houver automaÃ§Ã£o.
4. A validaÃ§Ã£o apresentar evidÃªncia reproduzÃ­vel.
5. A matriz de conformidade for atualizada.

## 5. ObservaÃ§Ã£o de governanÃ§a

Nenhuma regra ainda nÃ£o confirmada deverÃ¡ ser transformada em correÃ§Ã£o automÃ¡tica dos dados.

A equipe deverÃ¡ preservar os valores originais, registrar as incertezas e separar:
- erro tÃ©cnico comprovado;
- inconsistÃªncia potencial;
- ausÃªncia de informaÃ§Ã£o;
- regra de negÃ³cio pendente de confirmaÃ§Ã£o.

**PrÃ³xima etapa:** encaminhar as sete questÃµes Ã  CESIC e registrar formalmente as respostas antes da consolidaÃ§Ã£o das regras na prÃ³xima versÃ£o da pipeline.
