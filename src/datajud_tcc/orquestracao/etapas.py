"""Etapas Silver e Gold chamadas pelos fluxos.

Ficam separadas dos fluxos para que a implementação (PostgreSQL, docs/artigo/10)
possa ser trocada ou simulada nos testes sem alterar a orquestração.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def carregar_silver(run_root: Path, conn: Any = None) -> dict[str, int]:
    """Carrega uma execução da Bronze na Silver; retorna contagens por tabela.

    Sem `conn`, abre a conexão, aplica o esquema, faz commit e fecha. Com `conn`,
    o chamador controla a transação (nenhum commit aqui).
    """
    from datajud_tcc.silver import carga, conexao, esquema

    if conn is not None:
        return carga.carregar_execucao(conn, Path(run_root))
    propria = conexao.conectar()
    try:
        esquema.aplicar_esquema(propria)
        contagens = carga.carregar_execucao(propria, Path(run_root))
        propria.commit()
        return contagens
    except BaseException:
        propria.rollback()
        raise
    finally:
        propria.close()


def construir_gold(versao_regras: str, conn: Any = None) -> dict[str, Any]:
    """Reconstrói a Gold. Sem `conn`, conecta, faz commit e fecha; com `conn`, sem commit."""
    from datajud_tcc.gold import construcao
    from datajud_tcc.silver import conexao

    if conn is not None:
        return construcao.construir_gold(conn, versao_regras)
    propria = conexao.conectar()
    try:
        contagens = construcao.construir_gold(propria, versao_regras)
        propria.commit()
        return contagens
    except BaseException:
        propria.rollback()
        raise
    finally:
        propria.close()


