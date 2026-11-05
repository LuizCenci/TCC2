"""Etapas Silver e Gold chamadas pelos fluxos.

Ficam separadas dos fluxos para que a implementação (PostgreSQL, docs/artigo/10)
possa ser trocada ou simulada nos testes sem alterar a orquestração.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def carregar_silver(run_root: Path) -> dict[str, Any]:
    """Carrega uma execução da Bronze na Silver; retorna contagens por tabela."""
    raise NotImplementedError("Silver ainda não implementada (docs/artigo/10-modelo-dados-silver.md)")


def construir_gold(versao_regras: str) -> dict[str, Any]:
    """Recalcula derivados e agregações para uma versão de regras."""
    raise NotImplementedError("Gold ainda não implementada (docs/artigo/10-modelo-dados-silver.md)")
