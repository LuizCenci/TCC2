import os
from pathlib import Path

import pytest

from datajud_tcc.catalog import Catalog
from datajud_tcc.client import DatajudClient
from datajud_tcc.config import CollectionConfig
from datajud_tcc.query import build_main_query


@pytest.mark.live
@pytest.mark.skipif(os.getenv("RUN_DATAJUD_LIVE") != "1", reason="live opt-in")
def test_tjpr_returns_valid_g1_page():
    api_key = os.getenv("DATAJUD_API_KEY", "")
    if not api_key.strip():
        pytest.fail("DATAJUD_API_KEY é obrigatória para o teste live")
    config = CollectionConfig.from_yaml(Path("config/collection.example.yaml"))
    catalog = Catalog.load(Path("config/catalogs/pvd_cnj_2025-07-17.yaml"))
    client = DatajudClient(
        endpoint=config.endpoint,
        api_key=api_key,
        connect_timeout_seconds=config.connect_timeout_seconds,
        read_timeout_seconds=config.read_timeout_seconds,
        max_attempts=config.max_attempts,
        max_wait_seconds=config.max_wait_seconds,
    )
    query = build_main_query(config, catalog, 2019)
    query["size"] = 1
    page = client.search(query)
    assert len(page.hits) <= 1
    assert all(hit["_source"].get("grau") == "G1" for hit in page.hits)
