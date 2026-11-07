"""Transformações SQL da Gold (Silver → gold.*)."""

import json
import logging
import time
from importlib import resources

from datajud_tcc.gold import qualidade, referencias, territorio
from datajud_tcc.gold.esquema import aplicar_esquema_gold

logger = logging.getLogger(__name__)


def executar_transformacoes(conn) -> None:
    """Executa gold/sql/*.sql em ordem lexicográfica; sem commit."""
    pasta = resources.files("datajud_tcc.gold").joinpath("sql")
    arquivos = sorted((p for p in pasta.iterdir() if p.name.endswith(".sql")),
                      key=lambda p: p.name)
    for arq in arquivos:
        conn.execute(arq.read_text(encoding="utf-8"))


def construir_gold(conn, versao_regras: str) -> dict:
    """Reconstrói a Gold por inteiro (idempotente); sem commit.

    Cada SQL de transformação já faz TRUNCATE da própria saída, então não há
    TRUNCATE adicional aqui.
    """
    esperada = referencias.ler_regras()["versao_regras"]
    if versao_regras != esperada:
        raise ValueError(f"versão de regras divergente: {versao_regras!r} != {esperada!r}")
    referencias.validar()

    def etapa(nome, fn):
        t = time.monotonic()
        r = fn()
        logger.info("gold %s concluída em %.1fs", nome, time.monotonic() - t)
        return r

    etapa("esquema", lambda: aplicar_esquema_gold(conn))
    etapa("referencias", lambda: referencias.carregar_referencias(conn))
    etapa("territorio", lambda: territorio.carregar_territorio(conn))
    etapa("transformacoes", lambda: executar_transformacoes(conn))
    q = qualidade.resumo(conn)
    contagens = {
        "versao_regras": versao_regras,
        "processos": conn.execute("SELECT count(*) FROM gold.fato_processo").fetchone()[0],
        "eventos": conn.execute("SELECT count(*) FROM gold.fato_evento").fetchone()[0],
        "categorias": conn.execute("SELECT count(*) FROM gold.processo_categoria").fetchone()[0],
        **q,
    }
    conn.execute(
        "INSERT INTO controle.execucao_gold (versao_regras, contagens) VALUES (%s, %s)",
        (versao_regras, json.dumps(contagens)))
    return contagens
