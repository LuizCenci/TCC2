from pathlib import Path

from datajud_tcc.catalog import Catalog
from datajud_tcc.config import CollectionConfig
from datajud_tcc.query import build_main_query

from .test_config import valid_mapping

CATALOGO = Path("config/catalogs/tjpr_vcm_2026-10-18.yaml")


def test_incremental_query_filters_by_last_update(tmp_path):
    mapping = valid_mapping(tmp_path) | {"updated_since": "2026-10-05T18:00:31.594Z"}
    config = CollectionConfig.from_mapping(mapping)
    filters = build_main_query(config, Catalog.load(CATALOGO), 2019)["query"]["bool"]["filter"]
    assert {"range": {"dataHoraUltimaAtualizacao": {"gt": "2026-10-05T18:00:31.594Z"}}} in filters


def test_regular_query_has_no_last_update_filter(tmp_path):
    config = CollectionConfig.from_mapping(valid_mapping(tmp_path))
    filters = build_main_query(config, Catalog.load(CATALOGO), 2019)["query"]["bool"]["filter"]
    assert not any("dataHoraUltimaAtualizacao" in str(f) for f in filters)
