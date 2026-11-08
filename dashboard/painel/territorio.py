"""Geometria e nomes das mesorregiões do Paraná."""
import json
from functools import cache

from painel.config import ARQUIVO_MESORREGIOES


@cache
def carregar_mesorregioes() -> dict:
    return json.loads(ARQUIVO_MESORREGIOES.read_text(encoding="utf-8"))


@cache
def NOMES_MESORREGIAO() -> dict[int, str]:
    return {f["properties"]["mesorregiao_id"]: f["properties"]["mesorregiao"]
            for f in carregar_mesorregioes()["features"]}
