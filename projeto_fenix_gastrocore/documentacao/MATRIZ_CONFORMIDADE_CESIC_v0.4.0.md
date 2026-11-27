# MATRIZ DE CONFORMIDADE CESIC
**Projeto:** Fenix GastroCore
**Camada:** Silver
**VersÃ£o:** 0.4.0
**Status:** Documento tÃ©cnico de trabalho â€” pendente de validaÃ§Ã£o da CESIC

## 1. Objetivo

Consolidar os resultados das verificaÃ§Ãµes realizadas sobre os dados da camada Silver, relacionando os critÃ©rios tÃ©cnicos e de negÃ³cio Ã s evidÃªncias disponÃ­veis.

Esta matriz nÃ£o representa homologaÃ§Ã£o das regras de negÃ³cio. Os itens que dependem de interpretaÃ§Ã£o ou confirmaÃ§Ã£o da CESIC permanecem identificados como pendentes.

## 2. Matriz de conformidade

| ID | CritÃ©rio | Resultado | EvidÃªncia / ObservaÃ§Ã£o |
|---|---|---|---|
| C01 | PreservaÃ§Ã£o dos dados Bronze | Conforme | Os cinco arquivos foram comparados com seus correspondentes Silver. |
| C02 | HigienizaÃ§Ã£o e padronizaÃ§Ã£o | Conforme tecnicamente | Pipeline aplica padronizaÃ§Ã£o de cabeÃ§alhos, textos e tratamento de marcadores de ausÃªncia. |
| C03 | ConversÃ£o e validaÃ§Ã£o de datas | Conforme | Campos de data avaliados apresentaram valores vÃ¡lidos. |
| C04 | PadronizaÃ§Ã£o de unidades | Parcial | Existem unidades que dependem de equivalÃªncia e interpretaÃ§Ã£o da CESIC. |
| C05 | Fator de correÃ§Ã£o (FC â‰¥ 1) | Conforme nos campos testados | VerificaÃ§Ãµes realizadas nos campos de fator de correÃ§Ã£o real e teÃ³rico. |
| C06 | Peso bruto â‰¥ peso limpo | Conforme | RelaÃ§Ã£o verificada nos registros de processamento de proteÃ­nas. |
| C07 | Integridade referencial | Parcial | RelaÃ§Ãµes avaliadas nÃ£o apresentaram chaves Ã³rfÃ£s; cobertura das relaÃ§Ãµes ainda nÃ£o Ã© integral. |
| C08 | InterpretaÃ§Ã£o de temperatura igual a zero | Pendente | Os 13 registros com temperatura zero precisam de interpretaÃ§Ã£o operacional. |
| C09 | Controle de lotes vencidos | NÃ£o verificÃ¡vel | Os arquivos analisados nÃ£o apresentam informaÃ§Ãµes suficientes de lote e validade. |
| C10 | Regra DA-1 | Parcial | Necessita confirmaÃ§Ã£o da definiÃ§Ã£o e dos critÃ©rios oficiais. |
| C11 | PreservaÃ§Ã£o dos campos originais | Conforme | ComparaÃ§Ã£o de 69 campos originais, sem divergÃªncias de valores nos cinco datasets. |
| C12 | ConsistÃªncia aritmÃ©tica do CMV | Conforme nos testes realizados | FÃ³rmulas e relaÃ§Ãµes aritmÃ©ticas implementadas foram verificadas. |
| C13 | ConsistÃªncia aritmÃ©tica de compras | Conforme nos testes realizados | Quantidade solicitada = entregue + pendente; valor total compatÃ­vel com quantidade e valor unitÃ¡rio, conforme tolerÃ¢ncia aplicada. |
| C14 | ComparaÃ§Ã£o entre perda e limite de perda | Conforme tecnicamente | Indicador descritivo de comparaÃ§Ã£o foi produzido, sem caracterizar automaticamente nÃ£o conformidade. |
| C15 | Unicidade das chaves internas | Parcial | A pipeline declara chaves para CMV, desperdÃ­cio e filiais, mas nÃ£o implementa validaÃ§Ã£o de unicidade para compras e processamento de proteÃ­nas. |

## 3. EvidÃªncias quantitativas

### 3.1 Integridade dos arquivos

| Dataset | Bronze | Silver | Campos originais divergentes |
|---|---:|---:|---:|
| CMV | 20 | 20 | 0 |
| DesperdÃ­cio | 30 | 30 | 0 |
| Filiais | 5 | 5 | 0 |
| Processamento de proteÃ­nas | 18 | 18 | 0 |
| RequisiÃ§Ãµes de compras | 18 | 18 | 0 |
| **Total** | **91** | **91** | **0** |

Foram preservados os registros e valores originais comparados. A camada Silver acrescentou cinco campos derivados: trÃªs relacionados Ã  temperatura e dois relacionados Ã  perda no processamento de proteÃ­nas.

### 3.2 Temperatura â€” desperdÃ­cio

Foram identificados 30 registros:

| ClassificaÃ§Ã£o tÃ©cnica atual | Quantidade |
|---|---:|
| ZERO_PENDENTE_INTERPRETACAO | 13 |
| ABAIXO_60C_REVISAR | 2 |
| SEM_ALERTA_NA_REGRA_APLICADA | 13 |
| NAO_APLICAVEL | 2 |
| **Total** | **30** |

Os 13 registros com temperatura zero correspondem a registros de Resto Ingesta. A interpretaÃ§Ã£o operacional do valor zero ainda depende de confirmaÃ§Ã£o.

Foram identificados dois registros de Sobra Limpa abaixo de 60Â°C:
- ID 4: 58,4Â°C.
- ID 17: 56,9Â°C.

Esses resultados representam alertas para revisÃ£o, nÃ£o uma conclusÃ£o automÃ¡tica sobre a causa ou a responsabilidade pelo ocorrido.

### 3.3 Processamento de proteÃ­nas

A comparaÃ§Ã£o entre perda percentual e limite de perda apresentou:

| Resultado da comparaÃ§Ã£o | Quantidade |
|---|---:|
| Acima do limite | 8 |
| Abaixo do limite | 8 |
| No limite | 2 |
| **Total** | **18** |

A classificaÃ§Ã£o Ã© descritiva. A interpretaÃ§Ã£o de conformidade depende da regra oficial aplicÃ¡vel ao produto e ao processo.

## 4. LimitaÃ§Ãµes tÃ©cnicas identificadas

A inspeÃ§Ã£o do cÃ³digo publicado da pipeline V2 identificou pontos que precisam de complementaÃ§Ã£o:

1. NÃ£o hÃ¡ validaÃ§Ã£o explÃ­cita automatizada para a soma de peso pÃ³s-descongelamento, aparas e rejeitos em relaÃ§Ã£o ao peso limpo.
2. NÃ£o hÃ¡ validaÃ§Ã£o explÃ­cita automatizada para perda total = peso bruto âˆ’ peso limpo.
3. NÃ£o hÃ¡ validaÃ§Ã£o explÃ­cita automatizada para percentual de perda = perda total / peso bruto Ã— 100.
4. Compras e processamento de proteÃ­nas ainda nÃ£o possuem validaÃ§Ã£o de unicidade de chaves na configuraÃ§Ã£o atual.
5. Algumas comparaÃ§Ãµes numÃ©ricas utilizam igualdade direta, podendo ser aprimoradas com tolerÃ¢ncias numÃ©ricas.
6. A integridade referencial ainda precisa contemplar todas as relaÃ§Ãµes e domÃ­nios relevantes.

**ObservaÃ§Ã£o:** as verificaÃ§Ãµes descritas como realizadas em anÃ¡lises anteriores nÃ£o devem ser confundidas com testes automatizados presentes no cÃ³digo publicado. A implementaÃ§Ã£o deverÃ¡ ser comprovada por cÃ³digo e relatÃ³rio de execuÃ§Ã£o.

## 5. Encaminhamento

A matriz deverÃ¡ ser submetida Ã  CESIC para validaÃ§Ã£o das regras de negÃ³cio pendentes.

ApÃ³s as respostas, recomenda-se:
- atualizar os critÃ©rios e seus respectivos status;
- revisar o dicionÃ¡rio de dados;
- implementar os testes aprovados na prÃ³xima versÃ£o da pipeline;
- executar novamente a validaÃ§Ã£o da camada Silver;
- atualizar os relatÃ³rios de qualidade e o dossiÃª tÃ©cnico.

**Status geral:** tecnicamente avaliado, com pendÃªncias de negÃ³cio e de automaÃ§Ã£o. NÃ£o homologado pela CESIC.
