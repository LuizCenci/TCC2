"""Deterministic Elasticsearch queries for annual Datajud partitions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence

from .catalog import Catalog
from .config import CollectionConfig


# O índice público do TJPR armazena dataAjuizamento como YYYYMMDDHHMMSS,
# diferente do ISO 8601 do glossário; limites ISO retornam zero registros.
# Ver docs/anotações tcc.md.
DATA_AJUIZAMENTO_FORMAT = "%Y%m%d%H%M%S"


def year_bounds(year: int) -> tuple[str, str]:
    if year < 2000 or year > 2100:
        raise ValueError("ano fora do intervalo permitido")
    return (
        datetime(year, 1, 1).strftime(DATA_AJUIZAMENTO_FORMAT),
        datetime(year + 1, 1, 1).strftime(DATA_AJUIZAMENTO_FORMAT),
    )


def _base_filters(config: CollectionConfig, catalog: Catalog, year: int) -> list[dict[str, Any]]:
    if year not in config.years:
        raise ValueError(f"ano não configurado: {year}")
    start, end = year_bounds(year)
    return [
        {"range": {"dataAjuizamento": {"gte": start, "lt": end}}},
        {"term": {"grau.keyword": config.grau}},
    ]


def _thematic_filter(catalog: Catalog) -> dict[str, Any]:
    subjects = list(catalog.subject_codes) + list(catalog.extension_subject_codes)
    classes = list(catalog.extension_class_codes)
    if not classes:
        return {"terms": {"assuntos.codigo": subjects}}
    # Registro entra se tiver algum assunto do catálogo OU uma classe de extensão.
    return {
        "bool": {
            "should": [
                {"terms": {"assuntos.codigo": subjects}},
                {"terms": {"classe.codigo": classes}},
            ],
            "minimum_should_match": 1,
        }
    }


def _with_pagination(body: dict[str, Any], search_after: Sequence[Any] | None) -> dict[str, Any]:
    if search_after is not None:
        body["search_after"] = list(search_after)
    return body


def build_main_query(
    config: CollectionConfig,
    catalog: Catalog,
    year: int,
    search_after: Sequence[Any] | None = None,
) -> dict[str, Any]:
    filters = _base_filters(config, catalog, year)
    filters.append(_thematic_filter(catalog))
    body: dict[str, Any] = {
        "size": config.page_size,
        "query": {"bool": {"filter": filters}},
        "sort": [{"id.keyword": {"order": "asc"}}],
        # Sem isto o Elasticsearch para de contar em 10.000 (relation=gte).
        "track_total_hits": True,
    }
    return _with_pagination(body, search_after)


def build_diagnostic_query(
    config: CollectionConfig,
    catalog: Catalog,
    year: int,
    search_after: Sequence[Any] | None = None,
) -> dict[str, Any]:
    if not catalog.diagnostic_classes:
        raise ValueError("catálogo sem classes diagnósticas; use a consulta main")
    filters = _base_filters(config, catalog, year)
    filters.append({"terms": {"classe.codigo": list(catalog.diagnostic_classes)}})
    body: dict[str, Any] = {
        "size": config.page_size,
        "query": {
            "bool": {
                "filter": filters,
                "must_not": [{"terms": {"assuntos.codigo": list(catalog.subject_codes)}}],
            }
        },
        "sort": [{"id.keyword": {"order": "asc"}}],
        # Sem isto o Elasticsearch para de contar em 10.000 (relation=gte).
        "track_total_hits": True,
    }
    return _with_pagination(body, search_after)
