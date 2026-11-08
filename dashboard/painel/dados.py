"""Carga da exportação Gold com conferência de integridade."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from painel import config

COLUNAS_BOOL = [
    "ano_parcial", "suprimido", "suprimido_parcial",
    "estimavel", "mediana_alcancada", "orgao_especializado",
]
CHAVES_INT = {"ano_ajuizamento", "mes_ajuizamento", "mesorregiao_id", "orgao_codigo"}


class ErroIntegridade(Exception):
    pass


def _pasta(pasta: Path | None) -> Path:
    return pasta if pasta is not None else config.PASTA_EXPORTACAO


def carregar_manifesto(pasta: Path | None = None) -> dict:
    return json.loads((_pasta(pasta) / "manifesto.json").read_text(encoding="utf-8"))


def verificar_integridade(pasta: Path | None = None) -> None:
    pasta = _pasta(pasta)
    for item in carregar_manifesto(pasta)["arquivos"]:
        alvo = pasta / item["arquivo"]
        if not alvo.exists():
            raise ErroIntegridade(f"Arquivo ausente: {item['arquivo']}")
        if hashlib.sha256(alvo.read_bytes()).hexdigest() != item["sha256"]:
            raise ErroIntegridade(f"SHA-256 divergente: {item['arquivo']}")


def carregar_tabela(nome: str, pasta: Path | None = None) -> pd.DataFrame:
    df = pd.read_csv(_pasta(pasta) / f"{nome}.csv", dtype=str, keep_default_na=False)
    for col in COLUNAS_BOOL:
        if col in df.columns:
            df[col] = df[col].str.strip().str.lower().eq("true")
    for col in df.columns:
        if col in COLUNAS_BOOL:
            continue
        if col in CHAVES_INT or col == "n" or col.startswith("n_") or col == "pop_feminina":
            df[col] = pd.to_numeric(df[col].replace("", pd.NA)).astype("Int64")
        elif col.startswith(("taxa_", "media", "mediana_dias", "ic95", "pct", "ia_")):
            df[col] = pd.to_numeric(df[col].replace("", pd.NA))
    return df


def total_processos(pasta: Path | None = None) -> int:
    df = carregar_tabela("agg_pipeline", pasta)
    linha = df[df["versao_regras"] != ""]
    return int(linha["n"].iloc[0])
