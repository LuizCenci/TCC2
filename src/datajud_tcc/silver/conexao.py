"""Conexão com o PostgreSQL local, somente via DATABASE_URL."""

from __future__ import annotations

import os


def obter_dsn() -> str:
    """Lê DATABASE_URL do ambiente ou do `.env`; nunca expõe o valor em erros."""
    if not os.getenv("DATABASE_URL", "").strip():
        from datajud_tcc.cli import _load_dotenv

        _load_dotenv(chave="DATABASE_URL")
    dsn = os.getenv("DATABASE_URL", "").strip()
    if not dsn:
        raise RuntimeError("DATABASE_URL não configurado")
    return dsn


def conectar(dsn: str | None = None):
    """Abre conexão psycopg com autocommit desligado."""
    import psycopg

    return psycopg.connect(dsn or obter_dsn(), autocommit=False,
                           connect_timeout=10)
