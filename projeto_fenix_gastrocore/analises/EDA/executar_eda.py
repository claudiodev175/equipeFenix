# -*- coding: utf-8 -*-
"""
GastroCore | Automação da Análise Exploratória de Dados (EDA)
Lê os CSVs da camada Silver, sem modificá-los, e gera:
- auditoria estrutural e estatística;
- verificações de consistência específicas;
- gráficos exploratórios;
- relatórios Markdown individuais e consolidado;
- CSVs auxiliares com estatísticas.

Execução a partir da raiz de projeto_fenix_gastrocore:
    python .\analises\EDA\executar_eda.py
"""

from pathlib import Path
import json
import sys
import warnings

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=FutureWarning)

# ---------------------------------------------------------------------
# 1. Localização automática das pastas
# ---------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

POSSIBLE_SILVER_DIRS = [
    PROJECT_ROOT / "data" / "silver",
    PROJECT_ROOT / "silver",
    PROJECT_ROOT.parent / "data" / "silver",
]

SILVER_DIR = next((p for p in POSSIBLE_SILVER_DIRS if p.exists()), None)
if SILVER_DIR is None:
    print("ERRO: não encontrei a pasta data/silver.")
    print("Esperado: projeto_fenix_gastrocore/data/silver/")
    sys.exit(1)

REPORT_DIR = SCRIPT_DIR / "relatorios"
GRAPH_DIR = SCRIPT_DIR / "graficos"
RESULT_DIR = SCRIPT_DIR / "resultados"
for folder in (REPORT_DIR, GRAPH_DIR, RESULT_DIR):
    folder.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "consumo_cmv": "gastrocore_consumo_cmv_silver.csv",
    "desperdicio": "gastrocore_desperdicio_rdc216_silver.csv",
    "filiais": "gastrocore_filiais_pe_silver.csv",
    "processamento_proteinas": "gastrocore_processamento_proteinas_silver.csv",
    "requisicoes_compras": "gastrocore_requisicoes_compras_silver.csv",
}

# ---------------------------------------------------------------------
# 2. Funções auxiliares
# ---------------------------------------------------------------------
def read_csv(path):
    # Os arquivos do projeto são CSVs UTF-8; fallback cobre exportações Windows.
    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin-1")


def safe_name(value):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in str(value))[:55]


def markdown_table(df, max_rows=30):
    if df.empty:
        return "_Sem registros para apresentar._"
    try:
        return df.head(max_rows).to_markdown(index=False)
    except Exception:
        return "```text\n" + df.head(max_rows).to_string(index=False) + "\n```"


def numeric_columns(df):
    return list(df.select_dtypes(include=[np.number]).columns)


def save_numeric_histograms(df, dataset_key):
    cols = numeric_columns(df)
    # Evita gráficos excessivos e seleciona até quatro variáveis numéricas.
    for col in cols[:4]:
        values = pd.to_numeric(df[col], errors="coerce").dropna()
        if values.empty or values.nunique() < 2:
            continue
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.hist(values, bins=min(12, max(5, values.nunique())), edgecolor="black")
        ax.set_title(f"{dataset_key}: distribuição de {col}")
        ax.set_xlabel(col)
        ax.set_ylabel("Frequência")
        ax.grid(axis="y", alpha=0.25)
        fig.tight_layout()
        fig.savefig(GRAPH_DIR / f"{dataset_key}_{safe_name(col)}_hist.png", dpi=150)
        plt.close(fig)


def save_top_category_chart(df, dataset_key):
    candidates = [
        c for c in df.columns
        if df[c].dtype == "object" and 2 <= df[c].nunique(dropna=True) <= 15
    ]
    if not candidates:
        return
    # Prioriza campos com significado operacional.
    preferred = [
        "categoria_insumo", "tipo_descarte", "regiao", "tipo_proteina",
        "status_perda", "categoria_item", "unidade_medida", "status_operacional"
    ]
    col = next((c for c in preferred if c in candidates), candidates[0])
    counts = df[col].fillna("(ausente)").value_counts().head(12).sort_values()
    fig, ax = plt.subplots(figsize=(8, 4.5))
    counts.plot(kind="barh", ax=ax)
    ax.set_title(f"{dataset_key}: frequência por {col}")
    ax.set_xlabel("Quantidade de registros")
    ax.set_ylabel(col)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(GRAPH_DIR / f"{dataset_key}_{safe_name(col)}_frequencia.png", dpi=150)
    plt.close(fig)


def check_sum(df, left, right, result, label, tolerance=0.01):
    if all(c in df.columns for c in (left, right, result)):
        a = pd.to_numeric(df[left], errors="coerce")
        b = pd.to_numeric(df[right], errors="coerce")
        c = pd.to_numeric(df[result], errors="coerce")
        diff = (a + b - c).abs()
        valid = diff.notna()
        return {
            "verificacao": label,
            "registros_verificados": int(valid.sum()),
            "divergencias": int((diff[valid] > tolerance).sum()),
            "maior_diferenca": round(float(diff[valid].max()), 6) if valid.any() else None,
            "tolerancia": tolerance,
        }
    return None


def specific_checks(key, df):
    checks = []
    if key == "consumo_cmv":
        for c in ["qtd_prevista_kg", "qtd_real_kg", "cmv_orcado_reais",
                  "cmv_realizado_reais", "desvio_cmv_reais"]:
            if c in df:
                checks.append({
                    "verificacao": f"{c}: valores negativos",
                    "registros_verificados": int(df[c].notna().sum()),
                    "divergencias": int((pd.to_numeric(df[c], errors="coerce") < 0).sum()),
                    "maior_diferenca": None, "tolerancia": 0
                })
        if {"cmv_realizado_reais", "cmv_orcado_reais", "desvio_cmv_reais"}.issubset(df.columns):
            diff = (df["cmv_realizado_reais"] - df["cmv_orcado_reais"] - df["desvio_cmv_reais"]).abs()
            checks.append({
                "verificacao": "CMV realizado - CMV orçado = desvio",
                "registros_verificados": int(diff.notna().sum()),
                "divergencias": int((diff > 0.01).sum()),
                "maior_diferenca": round(float(diff.max()), 6), "tolerancia": 0.01
            })

    elif key == "desperdicio":
        if "temp_afericao_celsius" in df:
            temp = pd.to_numeric(df["temp_afericao_celsius"], errors="coerce")
            checks.extend([
                {"verificacao": "Temperatura igual a zero (investigar significado)",
                 "registros_verificados": int(temp.notna().sum()),
                 "divergencias": int((temp == 0).sum()), "maior_diferenca": None,
                 "tolerancia": None},
                {"verificacao": "Temperatura positiva inferior a 60°C (investigar regra aplicável)",
                 "registros_verificados": int(temp.notna().sum()),
                 "divergencias": int(((temp > 0) & (temp < 60)).sum()),
                 "maior_diferenca": None, "tolerancia": None}
            ])
        if "indicador_temperatura_zero" in df:
            checks.append({"verificacao": "Registros marcados com indicador de temperatura zero",
                           "registros_verificados": int(df["indicador_temperatura_zero"].notna().sum()),
                           "divergencias": int(df["indicador_temperatura_zero"].astype(str).str.lower().isin(["1","true","sim","yes"]).sum()),
                           "maior_diferenca": None, "tolerancia": None})

    elif key == "processamento_proteinas":
        if {"peso_bruto_kg", "peso_limpo_kg", "perda_total_kg"}.issubset(df.columns):
            diff = (pd.to_numeric(df["peso_bruto_kg"], errors="coerce") -
                    pd.to_numeric(df["peso_limpo_kg"], errors="coerce") -
                    pd.to_numeric(df["perda_total_kg"], errors="coerce")).abs()
            checks.append({"verificacao": "Peso bruto - peso limpo = perda total",
                           "registros_verificados": int(diff.notna().sum()),
                           "divergencias": int((diff > 0.01).sum()),
                           "maior_diferenca": round(float(diff.max()), 6), "tolerancia": 0.01})
        if {"peso_bruto_kg", "peso_pos_descong_kg", "apara_kg", "rejeito_kg", "peso_limpo_kg"}.issubset(df.columns):
            diff = (pd.to_numeric(df["peso_pos_descong_kg"], errors="coerce") -
                    pd.to_numeric(df["apara_kg"], errors="coerce") -
                    pd.to_numeric(df["rejeito_kg"], errors="coerce") -
                    pd.to_numeric(df["peso_limpo_kg"], errors="coerce")).abs()
            checks.append({"verificacao": "Pós-descongelamento - aparas - rejeitos = peso limpo",
                           "registros_verificados": int(diff.notna().sum()),
                           "divergencias": int((diff > 0.01).sum()),
                           "maior_diferenca": round(float(diff.max()), 6), "tolerancia": 0.01})
        if {"perda_total_kg", "peso_bruto_kg", "perda_pct"}.issubset(df.columns):
            calc = (pd.to_numeric(df["perda_total_kg"], errors="coerce") /
                    pd.to_numeric(df["peso_bruto_kg"], errors="coerce") * 100)
            diff = (calc - pd.to_numeric(df["perda_pct"], errors="coerce")).abs()
            checks.append({"verificacao": "Percentual de perda recalculado (tolerância 0,01 p.p.)",
                           "registros_verificados": int(diff.notna().sum()),
                           "divergencias": int((diff > 0.01).sum()),
                           "maior_diferenca": round(float(diff.max()), 6), "tolerancia": 0.01})

    elif key == "requisicoes_compras":
        if {"qtd_solicitada", "qtd_entregue", "qtd_pendente"}.issubset(df.columns):
            diff = (pd.to_numeric(df["qtd_solicitada"], errors="coerce") -
                    pd.to_numeric(df["qtd_entregue"], errors="coerce") -
                    pd.to_numeric(df["qtd_pendente"], errors="coerce")).abs()
            checks.append({"verificacao": "Solicitada = entregue + pendente",
                           "registros_verificados": int(diff.notna().sum()),
                           "divergencias": int((diff > 0.01).sum()),
                           "maior_diferenca": round(float(diff.max()), 6), "tolerancia": 0.01})
        if {"qtd_solicitada", "valor_unit_estimado", "valor_total_estimado"}.issubset(df.columns):
            calc = pd.to_numeric(df["qtd_solicitada"], errors="coerce") * pd.to_numeric(df["valor_unit_estimado"], errors="coerce")
            diff = (calc - pd.to_numeric(df["valor_total_estimado"], errors="coerce")).abs()
            checks.append({"verificacao": "Quantidade solicitada x valor unitário = valor total estimado",
                           "registros_verificados": int(diff.notna().sum()),
                           "divergencias": int((diff > 0.02).sum()),
                           "maior_diferenca": round(float(diff.max()), 6), "tolerancia": 0.02})
    return [c for c in checks if c is not None]


def analyze_dataset(key, filename):
    path = SILVER_DIR / filename
    if not path.exists():
        return {"key": key, "error": f"Arquivo não encontrado: {path}"}

    df = read_csv(path)
    n_rows, n_cols = df.shape
    missing = df.isna().sum()
    duplicated = int(df.duplicated().sum())
    nums = df.select_dtypes(include=[np.number])
    stats = nums.describe().T.reset_index().rename(columns={"index": "variavel"})
    stats.to_csv(RESULT_DIR / f"{key}_estatisticas_numericas.csv", index=False, encoding="utf-8-sig")

    categorical = []
    for col in df.select_dtypes(include=["object", "category"]).columns:
        categorical.append({
            "variavel": col,
            "categorias_distintas": int(df[col].nunique(dropna=True)),
            "categoria_mais_frequente": str(df[col].mode(dropna=True).iloc[0]) if not df[col].mode(dropna=True).empty else "",
            "frequencia": int(df[col].value_counts(dropna=True).iloc[0]) if not df[col].value_counts(dropna=True).empty else 0
        })
    cat_df = pd.DataFrame(categorical)
    if not cat_df.empty:
        cat_df.to_csv(RESULT_DIR / f"{key}_frequencias_categoricas.csv", index=False, encoding="utf-8-sig")

    checks = specific_checks(key, df)
    checks_df = pd.DataFrame(checks)
    if not checks_df.empty:
        checks_df.to_csv(RESULT_DIR / f"{key}_verificacoes.csv", index=False, encoding="utf-8-sig")

    save_numeric_histograms(df, key)
    save_top_category_chart(df, key)

    # Correlações apenas para variáveis numéricas; associação não implica causalidade.
    corr_path = RESULT_DIR / f"{key}_correlacoes.csv"
    if nums.shape[1] >= 2:
        nums.corr(numeric_only=True).to_csv(corr_path, encoding="utf-8-sig")

    report = [
        f"# EDA — {key.replace('_', ' ').title()}",
        "",
        "## 1. Escopo",
        f"Arquivo analisado: `{filename}`.",
        "Análise exploratória descritiva da camada Silver. A base original não foi modificada.",
        "",
        "## 2. Diagnóstico estrutural",
        f"- Registros: **{n_rows}**",
        f"- Colunas: **{n_cols}**",
        f"- Valores ausentes: **{int(missing.sum())}**",
        f"- Linhas integralmente duplicadas: **{duplicated}**",
        "",
        "### Valores ausentes por variável",
        markdown_table(missing[missing > 0].rename_axis("variavel").reset_index(name="ausentes")),
        "",
        "## 3. Estatísticas descritivas — variáveis numéricas",
        markdown_table(stats.round(4)),
        "",
        "## 4. Perfil das variáveis categóricas",
        markdown_table(cat_df),
        "",
        "## 5. Verificações específicas",
        markdown_table(checks_df),
        "",
        "## 6. Gráficos",
    ]
    images = sorted(GRAPH_DIR.glob(f"{key}_*.png"))
    if images:
        for img in images:
            report.append(f"![{img.stem}](../graficos/{img.name})")
            report.append("")
    else:
        report.append("_Não foram gerados gráficos para este conjunto._")
    report += [
        "## 7. Interpretação e limitações",
        "- Estatísticas e frequências descrevem somente os registros disponíveis nesta base.",
        "- Amostras pequenas ou sintéticas não permitem generalização para toda a operação.",
        "- Correlações são exploratórias e não demonstram causalidade.",
        "- Regras de negócio, limites operacionais e semântica de campos devem ser confirmados pelo CESIC.",
        "- Quantidades com unidades de medida diferentes não devem ser agregadas sem conversão validada.",
        "",
        "## 8. Próximas verificações recomendadas",
        "- Confirmar dicionário de dados, unidades de medida e regras de negócio.",
        "- Validar chaves de negócio e relacionamentos com as demais tabelas.",
        "- Confirmar períodos de referência antes de comparações entre bases.",
        "",
        "---",
        "Relatório gerado automaticamente pelo script `executar_eda.py`.",
    ]
    report_path = REPORT_DIR / f"EDA_{key}.md"
    report_path.write_text("\n".join(report), encoding="utf-8")

    return {
        "key": key, "arquivo": filename, "registros": n_rows, "colunas": n_cols,
        "ausentes": int(missing.sum()), "duplicadas": duplicated,
        "verificacoes": checks, "relatorio": str(report_path)
    }


# ---------------------------------------------------------------------
# 3. Execução geral e relatório consolidado
# ---------------------------------------------------------------------
def main():
    print(f"Projeto: {PROJECT_ROOT}")
    print(f"Silver:  {SILVER_DIR}")
    print("Iniciando EDA das cinco bases...\n")

    results = []
    for key, filename in DATASETS.items():
        print(f"[{key}]")
        result = analyze_dataset(key, filename)
        results.append(result)
        if "error" in result:
            print("  ERRO:", result["error"])
        else:
            print(f"  {result['registros']} registros | {result['colunas']} colunas | "
                  f"{result['ausentes']} ausentes | {result['duplicadas']} duplicadas")

    valid = [r for r in results if "error" not in r]
    summary = pd.DataFrame([{
        "base": r["key"], "arquivo": r["arquivo"], "registros": r["registros"],
        "colunas": r["colunas"], "valores_ausentes": r["ausentes"],
        "linhas_duplicadas": r["duplicadas"]
    } for r in valid])
    summary.to_csv(RESULT_DIR / "resumo_geral_eda.csv", index=False, encoding="utf-8-sig")

    consolidated = [
        "# GastroCore — Relatório Consolidado da EDA",
        "",
        "## Escopo",
        "Análise exploratória das bases disponíveis na camada Silver. Os arquivos de origem não foram alterados.",
        "",
        "## Resumo das bases",
        markdown_table(summary),
        "",
        f"**Total de registros analisados:** {int(summary['registros'].sum()) if not summary.empty else 0}",
        f"**Total de colunas analisadas:** {int(summary['colunas'].sum()) if not summary.empty else 0}",
        f"**Total de valores ausentes:** {int(summary['valores_ausentes'].sum()) if not summary.empty else 0}",
        f"**Total de linhas integralmente duplicadas:** {int(summary['linhas_duplicadas'].sum()) if not summary.empty else 0}",
        "",
        "## Relatórios individuais",
    ]
    for r in valid:
        consolidated.append(f"- [EDA {r['key']}](EDA_{r['key']}.md)")
    consolidated += [
        "",
        "## Ressalvas transversais",
        "- Ausência de valores nulos ou duplicatas integrais não comprova validade semântica.",
        "- As bases têm granularidades, períodos e unidades diferentes; não devem ser combinadas sem regras explícitas.",
        "- A base de filiais contém cadastro de unidades e não deve ser interpretada como amostra operacional equivalente às demais.",
        "- Correlações e associações não demonstram causalidade.",
        "- Os dados e as regras devem ser confirmados pelo CESIC antes de decisões operacionais ou homologação.",
        "",
        "## Limitações",
        "- Resultados restritos aos arquivos Silver fornecidos.",
        "- Não foram inferidos dados ausentes nem corrigidos valores de origem.",
        "- Verificações específicas são testes aritméticos/indicativos, não substituem validação formal das regras de negócio.",
        "",
        "## Status",
        "Relatório exploratório gerado automaticamente. Requer revisão técnica e validação das regras pelo CESIC.",
    ]
    (REPORT_DIR / "EDA_CONSOLIDADA.md").write_text("\n".join(consolidated), encoding="utf-8")

    (RESULT_DIR / "resultado_execucao.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )

    print("\nConcluído.")
    print(f"Relatórios: {REPORT_DIR}")
    print(f"Gráficos:   {GRAPH_DIR}")
    print(f"Resultados: {RESULT_DIR}")
    if len(valid) != len(DATASETS):
        print("ATENÇÃO: uma ou mais bases não foram encontradas. Confira os nomes dos CSVs.")
        sys.exit(2)


if __name__ == "__main__":
    main()
