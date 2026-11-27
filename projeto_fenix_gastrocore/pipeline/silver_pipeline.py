#!/usr/bin/env python
"""
Fenix GastroCore | Sprint 1 - Silver Data Quality V2
Executa limpeza conservadora, tipagem e auditoria dos cinco CSVs Bronze.

Uso:
    pip install pandas
    python silver_pipeline.py --input-dir . --output-dir data/silver

Os arquivos originais nunca são sobrescritos.
Valores suspeitos e conflitos de chave são reportados; não são apagados automaticamente.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


FILES = {
    "gastrocore_consumo_cmv.csv": {
        "date": ["data_competencia"],
        "integer": ["id_consumo", "id_filial"],
        "numeric": [
            "qtd_prevista_kg", "qtd_real_kg", "custo_unitario_kg",
            "cmv_orcado_reais", "cmv_realizado_reais", "desvio_cmv_reais",
            "desvio_cmv_percentual", "fator_correcao_teorico",
            "fator_correcao_real",
        ],
        "key": ["id_consumo"],
    },
    "gastrocore_desperdicio_rdc216.csv": {
        "date": ["data_registro"],
        "integer": ["id_registro", "id_filial", "refeicoes_produzidas_pax"],
        "numeric": [
            "peso_kg", "custo_estimado_reais",
            "resto_ingesta_por_pax_gramas", "temp_afericao_celsius",
        ],
        "key": ["id_registro"],
    },
    "gastrocore_filiais_pe.csv": {
        "date": [],
        "integer": ["id_filial", "capacidade_refeicoes_dia"],
        "numeric": ["meta_cmv_percentual"],
        "key": ["id_filial"],
    },
    "gastrocore_processamento_proteinas.csv": {
        "date": ["data_processamento"],
        "integer": [],
        "numeric": [
            "peso_bruto_kg", "peso_pos_descong_kg", "apara_kg",
            "rejeito_kg", "peso_limpo_kg", "perda_total_kg",
            "perda_pct", "fator_correcao_real", "limite_perda_pct",
        ],
        "key": [],
    },
    "gastrocore_requisicoes_compras.csv": {
        "date": ["data_solicitacao"],
        "integer": [],
        "numeric": [
            "saldo_estoque", "qtd_solicitada", "qtd_entregue",
            "qtd_pendente", "valor_unit_estimado", "valor_total_estimado",
        ],
        "key": [],
    },
}

NULL_TOKENS = {"", "null", "none", "nan", "n/a", "na", "nat"}



class IntegrityValidationError(Exception):
    """Falha na validação obrigatória da integridade da camada Bronze."""


def sha256_file(path: Path) -> str:
    """Calcula SHA-256 em blocos, sem carregar o arquivo inteiro na memória."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_bronze_manifest(input_dir: Path, manifest_path: Path) -> dict:
    """Valida o manifesto e os cinco CSVs antes de qualquer transformação."""
    if not manifest_path.is_file():
        raise IntegrityValidationError(
            f"Manifesto obrigatório não encontrado: {manifest_path}"
        )

    try:
        manifest = pd.read_csv(manifest_path, dtype="string", keep_default_na=False, encoding="utf-8-sig")
    except Exception as exc:
        raise IntegrityValidationError(f"Não foi possível ler o manifesto: {exc}") from exc

    required_columns = {
        "Arquivo", "SHA256_Bronze", "SHA256_Referencia", "Status", "SHA256_Pacote_ZIP"
    }
    missing_columns = sorted(required_columns - set(manifest.columns))
    if missing_columns:
        raise IntegrityValidationError(
            "Manifesto sem colunas obrigatórias: " + ", ".join(missing_columns)
        )

    if manifest["Arquivo"].duplicated().any():
        duplicated = manifest.loc[manifest["Arquivo"].duplicated(keep=False), "Arquivo"].tolist()
        raise IntegrityValidationError(
            "Manifesto contém arquivos duplicados: " + ", ".join(duplicated)
        )

    expected_files = set(FILES)
    listed_files = set(manifest["Arquivo"].astype(str))
    missing_entries = sorted(expected_files - listed_files)
    unexpected_entries = sorted(listed_files - expected_files)
    if missing_entries or unexpected_entries:
        details = []
        if missing_entries:
            details.append("ausentes no manifesto: " + ", ".join(missing_entries))
        if unexpected_entries:
            details.append("não esperados no manifesto: " + ", ".join(unexpected_entries))
        raise IntegrityValidationError("Relação de arquivos do manifesto inválida (" + "; ".join(details) + ").")

    checked = []
    for filename in FILES:
        row = manifest.loc[manifest["Arquivo"] == filename].iloc[0]
        source = input_dir / filename
        if not source.is_file():
            raise IntegrityValidationError(f"Arquivo Bronze obrigatório não encontrado: {source}")

        recorded_bronze = str(row["SHA256_Bronze"]).strip().upper()
        recorded_reference = str(row["SHA256_Referencia"]).strip().upper()
        recorded_status = str(row["Status"]).strip().upper()
        if not re.fullmatch(r"[A-F0-9]{64}", recorded_bronze):
            raise IntegrityValidationError(f"SHA256_Bronze inválido no manifesto para {filename}.")
        if not re.fullmatch(r"[A-F0-9]{64}", recorded_reference):
            raise IntegrityValidationError(f"SHA256_Referencia inválido no manifesto para {filename}.")
        if recorded_status != "INTEGRO":
            raise IntegrityValidationError(
                f"Status do manifesto não é INTEGRO para {filename}: {recorded_status or '(vazio)'}."
            )
        if recorded_bronze != recorded_reference:
            raise IntegrityValidationError(
                f"O hash Bronze difere do hash de referência registrado no manifesto: {filename}."
            )

        current_hash = sha256_file(source)
        if current_hash != recorded_bronze:
            raise IntegrityValidationError(
                f"DIVERGÊNCIA SHA-256 em {filename}.\n"
                f"  Registrado: {recorded_bronze}\n"
                f"  Atual:      {current_hash}\n"
                "Processamento Silver cancelado; nenhum CSV foi transformado nesta execução."
            )

        checked.append({
            "arquivo": filename,
            "sha256_manifesto": recorded_bronze,
            "sha256_atual": current_hash,
            "status": "INTEGRO",
        })

    package_hashes = set(manifest["SHA256_Pacote_ZIP"].astype(str).str.strip().str.upper())
    if len(package_hashes) != 1 or not re.fullmatch(r"[A-F0-9]{64}", next(iter(package_hashes), "")):
        raise IntegrityValidationError(
            "SHA256_Pacote_ZIP está ausente, inválido ou inconsistente entre as linhas do manifesto."
        )

    return {
        "manifesto": str(manifest_path.resolve()),
        "metodo": "SHA-256",
        "arquivos_verificados": len(checked),
        "arquivos_integros": len(checked),
        "status": "APROVADO",
        "sha256_pacote_zip_registrado": next(iter(package_hashes)),
        "detalhes": checked,
    }

def clean_text(series: pd.Series) -> pd.Series:
    """Remove espaços periféricos e espaços repetidos; preserva acentos e conteúdo."""
    out = series.astype("string").str.strip()
    out = out.str.replace(r"\s+", " ", regex=True)
    return out.mask(out.str.casefold().isin(NULL_TOKENS))


def audit_and_transform(path: Path, output_dir: Path) -> dict:
    cfg = FILES[path.name]
    df = pd.read_csv(path, dtype="string", keep_default_na=False, encoding="utf-8-sig")
    original_rows = len(df)
    original_columns = list(df.columns)

    # Padronização conservadora dos nomes de campos.
    normalized = []
    for col in df.columns:
        name = col.strip().lower()
        name = re.sub(r"[^\w]+", "_", name, flags=re.UNICODE).strip("_")
        normalized.append(name)
    df.columns = normalized

    # Limpeza textual sem remover acentos ou alterar categorias de negócio.
    for col in df.columns:
        df[col] = clean_text(df[col])

    issues = []
    type_errors = {}
    missing_before = int(df.isna().sum().sum())

    # Tipagem explícita.
    for col in cfg["date"]:
        if col in df.columns:
            raw = df[col].copy()
            parsed = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
            bad = int((raw.notna() & parsed.isna()).sum())
            if bad:
                type_errors[col] = bad
            df[col] = parsed.dt.strftime("%Y-%m-%d").astype("string")

    for col in cfg["numeric"]:
        if col in df.columns:
            raw = df[col].copy()
            parsed = pd.to_numeric(raw, errors="coerce")
            bad = int((raw.notna() & parsed.isna()).sum())
            if bad:
                type_errors[col] = bad
            df[col] = parsed

    for col in cfg["integer"]:
        if col in df.columns:
            raw = df[col].copy()
            parsed = pd.to_numeric(raw, errors="coerce")
            non_integer = parsed.notna() & (parsed % 1 != 0)
            if non_integer.any():
                type_errors[col] = int(non_integer.sum())
                parsed = parsed.mask(non_integer)
            df[col] = parsed.astype("Int64")

    # Duplicidades: remover apenas linhas integralmente idênticas.
    exact_duplicate_count = int(df.duplicated(keep="first").sum())
    if exact_duplicate_count:
        df = df.drop_duplicates(keep="first").copy()

    # Conflitos em chaves declaradas: manter e sinalizar, sem escolher registro arbitrariamente.
    key_conflicts = {}
    for key in cfg["key"]:
        if key in df.columns:
            duplicated = df[key].notna() & df[key].duplicated(keep=False)
            if duplicated.any():
                key_conflicts[key] = int(duplicated.sum())

    # Regras de negócio aplicáveis às colunas existentes.
    rule_results = {}
    if {"peso_bruto_kg", "peso_limpo_kg"}.issubset(df.columns):
        invalid = (
            df["peso_bruto_kg"].notna()
            & df["peso_limpo_kg"].notna()
            & (df["peso_bruto_kg"] < df["peso_limpo_kg"])
        )
        rule_results["PB_GE_PL"] = {
            "invalid_rows": int(invalid.sum()),
            "rule": "peso_bruto_kg >= peso_limpo_kg",
        }

    for col in ["fator_correcao_real", "fator_correcao_teorico"]:
        if col in df.columns:
            invalid = df[col].notna() & (df[col] < 1)
            rule_results[f"{col}_GE_1"] = {
                "invalid_rows": int(invalid.sum()),
                "rule": f"{col} >= 1",
            }

    # Verificações adicionais de coerência, sem alterar dados.
    if {"qtd_solicitada", "qtd_entregue", "qtd_pendente"}.issubset(df.columns):
        comparable = df[["qtd_solicitada", "qtd_entregue", "qtd_pendente"]].notna().all(axis=1)
        invalid = comparable & (
            (df["qtd_entregue"] + df["qtd_pendente"] != df["qtd_solicitada"])
        )
        rule_results["QTD_SOLICITADA_EQ_ENTREGUE_MAIS_PENDENTE"] = {
            "invalid_rows": int(invalid.sum()),
            "rule": "qtd_solicitada = qtd_entregue + qtd_pendente",
        }

    if {"peso_bruto_kg", "peso_limpo_kg", "fator_correcao_real"}.issubset(df.columns):
        comparable = (
            df["peso_bruto_kg"].notna()
            & df["peso_limpo_kg"].notna()
            & df["fator_correcao_real"].notna()
            & (df["peso_limpo_kg"] != 0)
        )
        calculated = df["peso_bruto_kg"] / df["peso_limpo_kg"]
        diff = (calculated - df["fator_correcao_real"]).abs()
        invalid = comparable & (diff > 0.02)
        rule_results["FC_REAL_COMPATIVEL_COM_PB_PL"] = {
            "invalid_rows": int(invalid.sum()),
            "rule": "fator_correcao_real aproximadamente igual a peso_bruto_kg / peso_limpo_kg (tolerância 0,02)",
        }

    # Controles complementares de consistência aritmética do CMV (sem corrigir valores).
    if {"qtd_prevista_kg", "custo_unitario_kg", "cmv_orcado_reais"}.issubset(df.columns):
        comparable = df[["qtd_prevista_kg", "custo_unitario_kg", "cmv_orcado_reais"]].notna().all(axis=1)
        diff = (df["qtd_prevista_kg"] * df["custo_unitario_kg"] - df["cmv_orcado_reais"]).abs()
        rule_results["CMV_ORCADO_ARITMETICAMENTE_COMPATIVEL"] = {
            "invalid_rows": int((comparable & (diff > 0.01)).sum()),
            "rule": "qtd_prevista_kg * custo_unitario_kg = cmv_orcado_reais (tolerância R$ 0,01)",
        }
    if {"qtd_real_kg", "custo_unitario_kg", "cmv_realizado_reais"}.issubset(df.columns):
        comparable = df[["qtd_real_kg", "custo_unitario_kg", "cmv_realizado_reais"]].notna().all(axis=1)
        diff = (df["qtd_real_kg"] * df["custo_unitario_kg"] - df["cmv_realizado_reais"]).abs()
        rule_results["CMV_REALIZADO_ARITMETICAMENTE_COMPATIVEL"] = {
            "invalid_rows": int((comparable & (diff > 0.01)).sum()),
            "rule": "qtd_real_kg * custo_unitario_kg = cmv_realizado_reais (tolerância R$ 0,01)",
        }
    if {"cmv_orcado_reais", "cmv_realizado_reais", "desvio_cmv_reais"}.issubset(df.columns):
        comparable = df[["cmv_orcado_reais", "cmv_realizado_reais", "desvio_cmv_reais"]].notna().all(axis=1)
        diff = (df["cmv_realizado_reais"] - df["cmv_orcado_reais"] - df["desvio_cmv_reais"]).abs()
        rule_results["DESVIO_CMV_ARITMETICAMENTE_COMPATIVEL"] = {
            "invalid_rows": int((comparable & (diff > 0.01)).sum()),
            "rule": "cmv_realizado_reais - cmv_orcado_reais = desvio_cmv_reais (tolerância R$ 0,01)",
        }
    if {"desvio_cmv_reais", "cmv_orcado_reais", "desvio_cmv_percentual"}.issubset(df.columns):
        comparable = df[["desvio_cmv_reais", "cmv_orcado_reais", "desvio_cmv_percentual"]].notna().all(axis=1) & (df["cmv_orcado_reais"] != 0)
        calculated = df["desvio_cmv_reais"] / df["cmv_orcado_reais"] * 100
        diff = (calculated - df["desvio_cmv_percentual"]).abs()
        rule_results["PERCENTUAL_DESVIO_CMV_COMPATIVEL"] = {
            "invalid_rows": int((comparable & (diff > 0.01)).sum()),
            "rule": "desvio_cmv_reais / cmv_orcado_reais * 100 = desvio_cmv_percentual (tolerância 0,01 ponto percentual)",
        }

    # Consistência aritmética do valor total de compras.
    if {"qtd_solicitada", "valor_unit_estimado", "valor_total_estimado"}.issubset(df.columns):
        comparable = df[["qtd_solicitada", "valor_unit_estimado", "valor_total_estimado"]].notna().all(axis=1)
        diff = (df["qtd_solicitada"] * df["valor_unit_estimado"] - df["valor_total_estimado"]).abs()
        rule_results["VALOR_TOTAL_COMPRA_COMPATIVEL"] = {
            "invalid_rows": int((comparable & (diff > 0.01)).sum()),
            "rule": "qtd_solicitada * valor_unit_estimado = valor_total_estimado (tolerância R$ 0,01)",
        }

    # Comparação de perda com limite informado na própria linha; campos de origem preservados.
    if {"perda_pct", "limite_perda_pct"}.issubset(df.columns):
        comparable = df[["perda_pct", "limite_perda_pct"]].notna().all(axis=1)
        delta = df["perda_pct"] - df["limite_perda_pct"]
        df["comparacao_limite_perda"] = pd.Series(pd.NA, index=df.index, dtype="string")
        df.loc[comparable & (delta > 0.000001), "comparacao_limite_perda"] = "ACIMA_DO_LIMITE"
        df.loc[comparable & (delta < -0.000001), "comparacao_limite_perda"] = "ABAIXO_DO_LIMITE"
        df.loc[comparable & (delta.abs() <= 0.000001), "comparacao_limite_perda"] = "NO_LIMITE"
        df["diferenca_limite_perda_pp"] = delta.where(comparable)
        rule_results["PERDA_PCT_COMPARADA_AO_LIMITE"] = {
            "acima_do_limite": int((comparable & (delta > 0.000001)).sum()),
            "abaixo_do_limite": int((comparable & (delta < -0.000001)).sum()),
            "no_limite": int((comparable & (delta.abs() <= 0.000001)).sum()),
            "regra": "comparação descritiva de perda_pct com limite_perda_pct; não altera status_perda original",
        }

    # Indicadores de temperatura: zero fica pendente de interpretação; limite de 60 °C
    # é aplicado somente a Sobra Limpa (Nao Distribuida), conforme auditoria exploratória.
    if {"tipo_descarte", "temp_afericao_celsius"}.issubset(df.columns):
        temp = df["temp_afericao_celsius"]
        zero = temp.eq(0).fillna(False)
        sobra_limpa = df["tipo_descarte"].eq("Sobra Limpa (Nao Distribuida)")
        abaixo_60 = sobra_limpa & temp.notna() & (temp < 60) & ~zero
        df["indicador_temperatura_zero"] = zero.astype("Int64")
        df["indicador_temperatura_abaixo_60"] = abaixo_60.astype("Int64")
        df["status_validacao_temperatura"] = pd.Series("NAO_APLICAVEL", index=df.index, dtype="string")
        df.loc[~zero & ~abaixo_60 & sobra_limpa, "status_validacao_temperatura"] = "SEM_ALERTA_NA_REGRA_APLICADA"
        df.loc[abaixo_60, "status_validacao_temperatura"] = "ABAIXO_60C_REVISAR"
        df.loc[zero, "status_validacao_temperatura"] = "ZERO_PENDENTE_INTERPRETACAO"
        rule_results["TEMPERATURA_ZERO_PENDENTE_INTERPRETACAO"] = {
            "ocorrencias": int(zero.sum()),
            "regra": "temperatura igual a zero é sinalizada; valor original preservado; não inferir ausência de aferição",
        }
        rule_results["SOBRA_LIMPA_ABAIXO_60C"] = {
            "ocorrencias": int(abaixo_60.sum()),
            "regra": "temperatura abaixo de 60 °C em Sobra Limpa (Nao Distribuida); indicador exploratório para revisão",
        }

    # Relatório de valores ausentes depois da tipagem.
    missing_by_column = {
        col: int(count)
        for col, count in df.isna().sum().items()
        if count > 0
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    out_name = path.stem + "_silver.csv"
    out_path = output_dir / out_name
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    return {
        "arquivo_origem": path.name,
        "arquivo_silver": out_name,
        "linhas_origem": original_rows,
        "linhas_silver": len(df),
        "colunas": len(df.columns),
        "colunas_originais": original_columns,
        "colunas_padronizadas": list(df.columns),
        "duplicatas_exatas_removidas": exact_duplicate_count,
        "conflitos_chave_mantidos_para_revisao": key_conflicts,
        "erros_de_conversao": type_errors,
        "valores_ausentes_por_coluna": missing_by_column,
        "regras": rule_results,
        "observacao": (
            "Registros com conflitos de chave ou violações de regra foram mantidos "
            "para revisão; somente duplicatas integralmente idênticas foram removidas."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default=".", help="Pasta com os cinco CSVs Bronze")
    parser.add_argument("--output-dir", default="data/silver", help="Pasta de saída Silver")
    parser.add_argument(
        "--manifest",
        default=None,
        help="Caminho do manifesto SHA-256 (padrão: <input-dir>/data/quality_reports/manifesto_integridade_bronze.csv)",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    manifest_path = (
        Path(args.manifest)
        if args.manifest
        else input_dir / "data" / "quality_reports" / "manifesto_integridade_bronze.csv"
    )

    # Barreira obrigatória: validar TODOS os arquivos antes de criar saídas ou transformar dados.
    try:
        integrity_report = validate_bronze_manifest(input_dir, manifest_path)
    except IntegrityValidationError as exc:
        print("ERRO DE INTEGRIDADE BRONZE — PIPELINE INTERROMPIDO", flush=True)
        print(str(exc), flush=True)
        raise SystemExit(2)

    print(
        f"Integridade Bronze aprovada: {integrity_report['arquivos_integros']}/5 arquivos íntegros.",
        flush=True,
    )

    report_dir = output_dir.parent / "quality_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for filename in FILES:
        source = input_dir / filename
        results.append(audit_and_transform(source, output_dir))

    report = {
        "projeto": "Fenix GastroCore",
        "etapa": "Sprint 1 - Silver Data Quality V2 - Quality Controls",
        "gerado_em_utc": datetime.now(timezone.utc).isoformat(),
        "integridade_bronze": integrity_report,
        "arquivos_processados": len(results),
        "arquivos_ausentes": [],
        "resultados": results,
        "politica": (
            "A validação SHA-256 do manifesto é obrigatória e ocorre antes da transformação. "
            "Preservar Bronze; não imputar valores ausentes; não corrigir valores suspeitos "
            "sem regra de negócio aprovada; conflitos de chave são sinalizados."
        ),
    }

    json_path = report_dir / "relatorio_quality_silver.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Fenix GastroCore — Relatório de Qualidade Silver",
        "",
        f"- Gerado em (UTC): {report['gerado_em_utc']}",
        f"- Arquivos processados: {len(results)}/5",
        "- Arquivos ausentes: Nenhum",
        "",
        "## Integridade da camada Bronze",
        "",
        f"- Manifesto: `{integrity_report['manifesto']}`",
        "- Método: SHA-256",
        f"- Arquivos verificados: {integrity_report['arquivos_verificados']}/5",
        f"- Resultado: **{integrity_report['status']}**",
        f"- SHA-256 do pacote ZIP registrado: `{integrity_report['sha256_pacote_zip_registrado']}`",
        "",
        "| Arquivo | Status | SHA-256 atual |",
        "|---|---|---|",
    ]
    for item in integrity_report["detalhes"]:
        lines.append(f"| {item['arquivo']} | {item['status']} | `{item['sha256_atual']}` |")
    lines += [
        "",
        "## Resultados por arquivo",
        "",
        "| Arquivo | Linhas Bronze | Linhas Silver | Duplicatas exatas removidas |",
        "|---|---:|---:|---:|",
    ]
    for r in results:
        lines.append(
            f"| {r['arquivo_origem']} | {r['linhas_origem']} | {r['linhas_silver']} | {r['duplicatas_exatas_removidas']} |"
        )
    for r in results:
        lines += ["", f"## {r['arquivo_origem']}", ""]
        lines.append(f"- Erros de conversão: `{r['erros_de_conversao'] or 'Nenhum'}`")
        lines.append(f"- Ausências: `{r['valores_ausentes_por_coluna'] or 'Nenhuma'}`")
        lines.append(f"- Conflitos de chave mantidos: `{r['conflitos_chave_mantidos_para_revisao'] or 'Nenhum'}`")
        lines.append(f"- Regras: `{r['regras'] or 'Nenhuma regra específica aplicável'}`")
    lines += [
        "",
        "## Política de tratamento",
        "",
        "- A validação SHA-256 do manifesto é obrigatória e antecede qualquer transformação.",
        "- Os arquivos Bronze não são sobrescritos.",
        "- Textos recebem remoção de espaços periféricos e repetidos; acentos e rótulos são preservados.",
        "- Datas e números recebem tipagem explícita.",
        "- Somente linhas integralmente duplicadas são removidas automaticamente.",
        "- Conflitos de chave, valores ausentes e violações de regra são reportados para revisão.",
        "- Nenhum valor ausente é imputado e nenhum valor suspeito é corrigido sem regra aprovada.",
        "",
        "## Limitações e pontos de atenção",
        "",
        "- Ruptura de estoque e lote vencido dependem de fonte com saldo mínimo, estoque atual e validade; não são inferidos dos cinco CSVs atuais.",
        "- PB >= PL e FC >= 1 são avaliados no arquivo de processamento de proteínas e nos campos de FC disponíveis.",
        "- A relação solicitada = entregue + pendente e o valor total estimado de compras são verificados aritmeticamente.",
        "- As fórmulas de CMV são verificações aritméticas complementares, com tolerância de R$ 0,01 e 0,01 ponto percentual.",
        "- A comparação de perda com limite é descritiva; status_perda original não é alterado.",
        "- Temperatura zero é sinalizada como pendente de interpretação; não é convertida em nulo.",
        "- O alerta abaixo de 60 °C é aplicado apenas a Sobra Limpa (Nao Distribuida), não a todos os tipos de descarte.",
    ]
    md_path = report_dir / "relatorio_quality_silver.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Arquivos Silver gerados: {len(results)}/5")
    print(f"Saída Silver: {output_dir.resolve()}")
    print(f"Relatório Markdown: {md_path.resolve()}")
    print(f"Relatório JSON: {json_path.resolve()}")


if __name__ == "__main__":
    main()
