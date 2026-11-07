"""Transformações SQL da Gold (Silver → gold.*)."""

from importlib import resources


def executar_transformacoes(conn) -> None:
    """Executa gold/sql/*.sql em ordem lexicográfica; sem commit."""
    pasta = resources.files("datajud_tcc.gold").joinpath("sql")
    arquivos = sorted((p for p in pasta.iterdir() if p.name.endswith(".sql")),
                      key=lambda p: p.name)
    for arq in arquivos:
        conn.execute(arq.read_text(encoding="utf-8"))
