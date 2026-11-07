"""Esquema versionado da Gold (ref, gold)."""

from importlib import resources


def _ler_ddl() -> str:
    return (
        resources.files("datajud_tcc.gold")
        .joinpath("esquema_gold.sql")
        .read_text(encoding="utf-8")
    )


def aplicar_esquema_gold(conn) -> None:
    """Executa esquema_gold.sql; idempotente e sem commit."""
    conn.execute(_ler_ddl())
