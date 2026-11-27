# -*- coding: utf-8 -*-
"""Regenera as visualizações gerenciais da base de desperdício GastroCore.

Executar a partir da raiz de projeto_fenix_gastrocore:
    python .\\analises\\EDA\\atualizar_graficos_desperdicio.py

Não altera os CSVs Silver. Remove apenas os quatro histogramas genéricos antigos
específicos de desperdício e substitui as referências no relatório EDA_desperdicio.md.
"""
from pathlib import Path
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
SILVER = PROJECT_ROOT / 'data' / 'silver' / 'gastrocore_desperdicio_rdc216_silver.csv'
GRAPH_DIR = SCRIPT_DIR / 'graficos'
REPORT = SCRIPT_DIR / 'relatorios' / 'EDA_desperdicio.md'

if not SILVER.exists():
    raise SystemExit(f'CSV Silver não encontrado: {SILVER}')
GRAPH_DIR.mkdir(parents=True, exist_ok=True)
df = pd.read_csv(SILVER, encoding='utf-8-sig')
required = {'tipo_descarte', 'peso_kg', 'custo_estimado_reais', 'temp_afericao_celsius', 'status_validacao_temperatura'}
missing = required - set(df.columns)
if missing:
    raise SystemExit(f'Colunas obrigatórias ausentes: {sorted(missing)}')

# 1) Volume de ocorrências por tipo de descarte
counts = df['tipo_descarte'].fillna('(não informado)').value_counts().sort_values()
fig, ax = plt.subplots(figsize=(10, 5.8))
bars = None
bars = ax.barh(counts.index, counts.values)
ax.bar_label(bars, padding=4, fmt='%.0f')
ax.set_title('Ocorrências de desperdício por tipo de descarte', loc='left', weight='bold', pad=14)
ax.set_xlabel('Número de registros')
ax.set_ylabel('Tipo de descarte')
ax.set_xlim(0, max(counts.values) * 1.18)
ax.grid(axis='x', alpha=.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(GRAPH_DIR / 'desperdicio_01_ocorrencias_por_tipo.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# 2) Custo estimado por tipo de descarte (soma monetária)
cost = df.groupby('tipo_descarte', dropna=False)['custo_estimado_reais'].sum().sort_values()
cost.index = cost.index.fillna('(não informado)')
fig, ax = plt.subplots(figsize=(10, 5.8))
bars = ax.barh(cost.index, cost.values)
ax.bar_label(bars, labels=[f'R$ {v:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') for v in cost.values], padding=5)
ax.set_title('Custo estimado acumulado por tipo de descarte', loc='left', weight='bold', pad=14)
ax.set_xlabel('Custo estimado (R$)')
ax.set_ylabel('Tipo de descarte')
ax.set_xlim(0, max(cost.values) * 1.25 if len(cost) else 1)
ax.grid(axis='x', alpha=.25)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig(GRAPH_DIR / 'desperdicio_02_custo_por_tipo.png', dpi=180, bbox_inches='tight')
plt.close(fig)

# 3) Temperaturas medidas e situa??o dos registros sem medi??o aplic?vel.
plot_df = df.copy()
plot_df["temp_num"] = pd.to_numeric(
    plot_df["temp_afericao_celsius"], errors="coerce"
)

sobra = plot_df[
    (plot_df["tipo_descarte"] == "Sobra Limpa (Nao Distribuida)")
    & (~plot_df["status_validacao_temperatura"].isin([
        "ZERO_PENDENTE_INTERPRETACAO", "NAO_APLICAVEL"
    ]))
    & plot_df["temp_num"].notna()
].copy()

zeros = plot_df[
    plot_df["status_validacao_temperatura"] == "ZERO_PENDENTE_INTERPRETACAO"
]
nao_aplicaveis = plot_df[
    plot_df["status_validacao_temperatura"] == "NAO_APLICAVEL"
]

revisar = sobra[
    sobra["status_validacao_temperatura"] == "ABAIXO_60C_REVISAR"
]

fig, (ax, ax2) = plt.subplots(
    1, 2, figsize=(13, 6.5),
    gridspec_kw={"width_ratios": [2.2, 1]}
)

# Painel A: temperaturas efetivamente registradas em Sobra Limpa.
x = np.arange(len(sobra))
cores = [
    "#C65D3A" if status == "ABAIXO_60C_REVISAR" else "#2878A5"
    for status in sobra["status_validacao_temperatura"]
]

ax.scatter(
    x, sobra["temp_num"], c=cores, s=90,
    edgecolors="white", linewidths=0.8, zorder=3
)

# Identifica??o textual somente dos registros sinalizados para revis?o.
for xi, (_, row) in zip(x, sobra.iterrows()):
    if row["status_validacao_temperatura"] == "ABAIXO_60C_REVISAR":
        ax.annotate(
            f'{row["id_registro"]}: {row["temp_num"]:.1f} ?C',
            (xi, row["temp_num"]),
            xytext=(8, -18), textcoords="offset points",
            fontsize=8, weight="bold"
        )

ax.axhline(
    60, color="#777777", linestyle="--", linewidth=1.4
)
ax.set_title("Sobra limpa ? temperaturas registradas", loc="left", weight="bold")
ax.set_xlabel("Identifica??o do registro")
ax.set_ylabel("Temperatura registrada (?C)")
ax.set_xticks(x)
ax.set_xticklabels(sobra["id_registro"].astype(str), rotation=45, ha="right")
ax.grid(axis="y", alpha=0.25)
ax.set_axisbelow(True)

from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="#2878A5", markersize=9,
           label="Demais medi??es"),
    Line2D([0], [0], marker="o", color="w",
           markerfacecolor="#C65D3A", markersize=9,
           label="Sinalizado para revis?o na base"),
    Line2D([0], [0], color="#777777", linestyle="--",
           label="Refer?ncia contextual: 60 ?C")
], loc="best", frameon=False, fontsize=8)

# Painel B: registros sem medi??o interpret?vel.
ax2.set_title("Registros sem medi??o aplic?vel", loc="left", weight="bold")
ax2.axis("off")

ax2.text(
    0.05, 0.82, "RESTO INGESTA",
    transform=ax2.transAxes, fontsize=10, weight="bold"
)
ax2.text(
    0.05, 0.68, f"{len(zeros)} registros",
    transform=ax2.transAxes, fontsize=22, weight="bold",
    color="#B7791F"
)
ax2.text(
    0.05, 0.57, "Valor zero: interpreta??o pendente",
    transform=ax2.transAxes, fontsize=9, wrap=True
)

ax2.text(
    0.05, 0.37, "PERDA EM PR?-PREPARO",
    transform=ax2.transAxes, fontsize=10, weight="bold"
)
ax2.text(
    0.05, 0.23, f"{len(nao_aplicaveis)} registros",
    transform=ax2.transAxes, fontsize=22, weight="bold",
    color="#666666"
)
ax2.text(
    0.05, 0.12, "Temperatura n?o aplic?vel",
    transform=ax2.transAxes, fontsize=9
)

fig.suptitle(
    "An?lise de temperatura por tipo de registro",
    fontsize=14, fontweight="bold", x=0.06, ha="left"
)
fig.text(
    0.06, 0.015,
    "Nota: 60 ?C ? refer?ncia contextual, n?o regra universal. "
    "Crit?rios de interpreta??o e aplica??o devem ser validados pelo CESIC.",
    fontsize=8.5, color="#555555"
)

fig.subplots_adjust(
    left=0.07, right=0.98, top=0.84, bottom=0.20, wspace=0.28
)
# Grava??o controlada e validada do gr?fico de temperatura.
output_path = (
    GRAPH_DIR / "desperdicio_03_temperatura_por_tipo.png"
).resolve()

GRAPH_DIR.mkdir(parents=True, exist_ok=True)

temporary_path = output_path.with_name(
    output_path.stem + "_temporario.png"
)

# Dimens?es fixas: evita depender do c?lculo autom?tico de bbox_inches.
fig.set_size_inches(13, 6.5, forward=True)
fig.canvas.draw()

try:
    fig.savefig(
        str(temporary_path),
        format="png",
        dpi=180
    )

    if not temporary_path.exists() or temporary_path.stat().st_size == 0:
        raise RuntimeError("O PNG tempor?rio n?o foi gerado corretamente.")

    # Verificar a integridade do arquivo antes de substituir o original.
    from PIL import Image

    with Image.open(temporary_path) as imagem:
        imagem.verify()

    # Substitui??o somente depois da valida??o.
    temporary_path.replace(output_path)

    print("Gr?fico de temperatura salvo e validado:")
    print(output_path)
    print("Tamanho:", output_path.stat().st_size, "bytes")

finally:
    if temporary_path.exists():
        temporary_path.unlink()

plt.close(fig)

plt.close(fig)

# Impedir que a próxima execução da EDA volte a criar gráficos genéricos para desperdício.
MAIN_SCRIPT = SCRIPT_DIR / 'executar_eda.py'
if MAIN_SCRIPT.exists():
    source = MAIN_SCRIPT.read_text(encoding='utf-8')
    old_calls = "    save_numeric_histograms(df, key)\n    save_top_category_chart(df, key)"
    new_calls = (
        "    if key != \"desperdicio\":\n"
        "        save_numeric_histograms(df, key)\n"
        "        save_top_category_chart(df, key)"
    )
    if old_calls in source:
        MAIN_SCRIPT.write_text(source.replace(old_calls, new_calls, 1), encoding='utf-8')
    elif new_calls not in source:
        raise SystemExit('Não foi possível localizar o bloco de geração genérica em executar_eda.py; nenhum patch aplicado.')

# Excluir somente os histogramas genéricos antigos desta base.
for old in GRAPH_DIR.glob('desperdicio_*_hist.png'):
    old.unlink()

# Atualizar a seção de gráficos do relatório individual sem alterar demais seções.
if REPORT.exists():
    content = REPORT.read_text(encoding='utf-8')
    start = content.find('## 6. Gráficos')
    end = content.find('## 7. Interpretação e limitações')
    if start >= 0 and end > start:
        section = '''## 6. Gráficos\n\n'''
        section += '### Ocorrências por tipo de descarte\n![Ocorrências por tipo de descarte](../graficos/desperdicio_01_ocorrencias_por_tipo.png)\n\n'
        section += '### Custo estimado por tipo de descarte\n![Custo por tipo de descarte](../graficos/desperdicio_02_custo_por_tipo.png)\n\n'
        section += '### Temperatura por tipo de registro\n![Temperatura por tipo de registro](../graficos/desperdicio_03_temperatura_por_tipo.png)\n\n'
        section += ('**Nota de interpretação:** valores iguais a zero estão identificados como pendentes de interpretação; '
                    'registros de pré-preparo possuem temperatura não aplicável. A referência de 60 °C é contextual e '
                    'não constitui classificação automática de irregularidade para todos os tipos de descarte. '
                    'A regra aplicável deve ser confirmada pelo CESIC.\n\n')
        REPORT.write_text(content[:start] + section + content[end:], encoding='utf-8')

print('Gráficos de desperdício atualizados com sucesso.')
print(f'Gráficos: {GRAPH_DIR}')
print(f'Relatório: {REPORT}')
print('CSV Silver preservado, sem alterações.')
print('\nResumo dos tipos:')
print(df.groupby('tipo_descarte').agg(registros=('id_registro','count'), peso_total_kg=('peso_kg','sum'), custo_total_reais=('custo_estimado_reais','sum')).to_string())
print('\nTemperaturas por status de validação:')
print(df.groupby('status_validacao_temperatura').agg(registros=('id_registro','count'), temperatura_min=('temp_afericao_celsius','min'), temperatura_max=('temp_afericao_celsius','max')).to_string())
