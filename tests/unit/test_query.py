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
                "gte": "2019-01-01T00:00:00Z",
                "lt": "2020-01-01T00:00:00Z",
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
