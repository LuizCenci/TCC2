"""Esquema versionado da Silver (controle, silver, restrito)."""

from importlib import resources


def _ler_ddl() -> str:
    return (
        resources.files("datajud_tcc.silver")
        .joinpath("esquema.sql")
        .read_text(encoding="utf-8")
    )


def aplicar_esquema(conn) -> None:
    """Executa esquema.sql; idempotente (IF NOT EXISTS) e sem commit.

    O script tem vários comandos e nenhum parâmetro, então o psycopg 3 o
    executa de uma só vez pelo protocolo simples, dentro da transação da
    conexão (o DDL do PostgreSQL é transacional).
    """
    conn.execute(_ler_ddl())
