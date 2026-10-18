from datajud_tcc.query import build_diagnostic_query, build_main_query

from .test_config import valid_mapping
from datajud_tcc.catalog import Catalog
from datajud_tcc.config import CollectionConfig


def objects(tmp_path):
    config = CollectionConfig.from_mapping(valid_mapping(tmp_path))
    catalog = Catalog.load(__import__("pathlib").Path("config/catalogs/pvd_cnj_2025-07-17.yaml"))
    return config, catalog


def test_2019_query_is_half_open_and_keeps_full_source(tmp_path):
    config, catalog = objects(tmp_path)
    query = build_main_query(config, catalog, 2019)
    filters = query["query"]["bool"]["filter"]
    assert {
        "range": {
            "dataAjuizamento": {
                "gte": "20190101000000",
                "lt": "20200101000000",
            }
        }
    } in filters
    assert {"term": {"grau.keyword": "G1"}} in filters
    assert query["size"] == 100
    assert query["sort"] == [{"id.keyword": {"order": "asc"}}]
    assert "_source" not in query


def test_search_after_is_added_without_mutating_base(tmp_path):
    config, catalog = objects(tmp_path)
    first = build_main_query(config, catalog, 2020)
    second = build_main_query(config, catalog, 2020, ["cursor-1"])
    assert "search_after" not in first
    assert second["search_after"] == ["cursor-1"]


def test_diagnostic_query_excludes_main_subjects(tmp_path):
    config, catalog = objects(tmp_path)
    query = build_diagnostic_query(config, catalog, 2021)
    filters = query["query"]["bool"]["filter"]
    assert {"terms": {"classe.codigo": [1268, 12423]}} in filters
    assert {"terms": {"assuntos.codigo": list(catalog.subject_codes)}} in query["query"]["bool"]["must_not"]


def test_queries_request_exact_total(tmp_path):
    config, catalog = objects(tmp_path)
    assert build_main_query(config, catalog, 2019)["track_total_hits"] is True
    assert build_diagnostic_query(config, catalog, 2019)["track_total_hits"] is True


def vcm_objects(tmp_path):
    config = CollectionConfig.from_mapping(valid_mapping(tmp_path))
    catalog = Catalog.load(__import__("pathlib").Path("config/catalogs/tjpr_vcm_2026-10-18.yaml"))
    return config, catalog


def test_main_query_with_extensions_matches_subjects_or_classes(tmp_path):
    config, catalog = vcm_objects(tmp_path)
    query = build_main_query(config, catalog, 2019)
    filters = query["query"]["bool"]["filter"]
    thematic = filters[-1]["bool"]
    assert thematic["minimum_should_match"] == 1
    assert {
        "terms": {"assuntos.codigo": list(catalog.subject_codes) + list(catalog.extension_subject_codes)}
    } in thematic["should"]
    assert {"terms": {"classe.codigo": list(catalog.extension_class_codes)}} in thematic["should"]
    assert {"term": {"grau.keyword": "G1"}} in filters
    assert "_source" not in query


def test_pvd_catalog_main_query_is_unchanged(tmp_path):
    config, catalog = objects(tmp_path)
    filters = build_main_query(config, catalog, 2019)["query"]["bool"]["filter"]
    assert {"terms": {"assuntos.codigo": list(catalog.subject_codes)}} in filters


def test_diagnostic_query_requires_diagnostic_classes(tmp_path):
    import pytest

    config, catalog = vcm_objects(tmp_path)
    with pytest.raises(ValueError, match="diagnóstic"):
        build_diagnostic_query(config, catalog, 2019)
