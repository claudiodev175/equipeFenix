ATUALIZAÇÃO DOS GRÁFICOS — GASTROCORE

1. Extraia atualizar_graficos_desperdicio.py para:
   projeto_fenix_gastrocore/analises/EDA/

2. Abra o terminal do VS Code na pasta projeto_fenix_gastrocore.

3. Execute:
   python .\analises\EDA\atualizar_graficos_desperdicio.py

O script:
- Gera gráfico de ocorrências por tipo de descarte.
- Gera gráfico de custo estimado acumulado por tipo de descarte.
- Gera gráfico de temperatura por tipo de registro, distinguindo valores zero pendentes de interpretação.
- Remove somente os histogramas genéricos antigos da base de desperdício.
- Atualiza a seção de gráficos do relatório EDA_desperdicio.md.
- Ajusta executar_eda.py para não recriar histogramas genéricos de desperdício nas próximas execuções.
- Não altera o CSV Silver.

Depois confira os arquivos em:
  analises/EDA/graficos/
  analises/EDA/relatorios/EDA_desperdicio.md

IMPORTANTE SOBRE TEMPERATURA:
- Os valores zero são exibidos como informação pendente de interpretação, não como temperatura medida nem como irregularidade.
- Registros de perda em pré-preparo estão identificados como não aplicáveis no status da base.
- A linha de 60 °C é uma referência visual contextual, não uma regra aplicada indistintamente a todos os tipos de descarte.
- A classificação e a regra sanitária aplicável devem ser confirmadas pelo CESIC.
