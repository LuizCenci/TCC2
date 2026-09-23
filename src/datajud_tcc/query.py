"""Deterministic Elasticsearch queries for annual Datajud partitions."""

from __future__ import annotations

from datetime import date
from typing import Any, Sequence

from .catalog import Catalog
from .config import CollectionConfig


def year_bounds(year: int) -> tuple[str, str]:
    if year < 2000 or year > 2100:
        raise ValueError("ano fora do intervalo permitido")
    return (
        f"{date(year, 1, 1).isoformat()}T00:00:00Z",
        f"{date(year + 1, 1, 1).isoformat()}T00:00:00Z",
    )


def _base_filters(config: CollectionConfig, catalog: Catalog, year: int) -> list[dict[str, Any]]:
    if year not in config.years:
        raise ValueError(f"ano não configurado: {year}")
    start, end = year_bounds(year)
    return [
        {"range": {"dataAjuizamento": {"gte": start, "lt": end}}},
        {"term": {"grau.keyword": config.grau}},
    ]


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
    filters.append({"terms": {"assuntos.codigo": list(catalog.subject_codes)}})
    body: dict[str, Any] = {
        "size": config.page_size,
        "query": {"bool": {"filter": filters}},
        "sort": [{"id.keyword": {"order": "asc"}}],
    }
    return _with_pagination(body, search_after)


def build_diagnostic_query(
    config: CollectionConfig,
    catalog: Catalog,
    year: int,
    search_after: Sequence[Any] | None = None,
) -> dict[str, Any]:
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
    }
    return _with_pagination(body, search_after)
