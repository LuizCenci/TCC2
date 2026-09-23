from dataclasses import replace
from pathlib import Path

import pytest

from datajud_tcc.catalog import Catalog
from datajud_tcc.client import InvalidResponseError, SearchPage
from datajud_tcc.collector import Collector
from datajud_tcc.config import CollectionConfig


def config(tmp_path, max_pages=1):
    return CollectionConfig.from_mapping(
        {
            "endpoint": "https://api.example.test/search",
            "tribunal": "TJPR",
            "grau": "G1",
            "years": [2019],
            "page_size": 100,
            "max_pages_per_partition": max_pages,
            "connect_timeout_seconds": 1,
            "read_timeout_seconds": 1,
            "max_attempts": 1,
            "max_wait_seconds": 1,
            "output_root": "work",
        }
    )


def catalog():
    return Catalog.load(Path("config/catalogs/pvd_cnj_2025-07-17.yaml"))


def page(count, start):
    hits = [
        {"_id": f"id-{i}", "_source": {"id": f"id-{i}"}, "sort": [f"id-{i}"]}
        for i in range(start, start + count)
    ]
    return SearchPage(
        raw={"hits": {"total": {"value": 101, "relation": "eq"}, "hits": hits}},
        hits=tuple(hits),
        next_cursor=[f"id-{start + count - 1}"] if hits else None,
        total={"value": 101, "relation": "eq"},
    )


class FakeClient:
    def __init__(self, pages=None, error=None):
        self.pages = list(pages or [])
        self.calls = []
        self.error = error

    def search(self, body):
        self.calls.append(body)
        if self.error:
            raise self.error
        return self.pages.pop(0)


def test_two_pages_use_cursor_and_complete_partition(tmp_path):
    client = FakeClient([page(100, 0), page(1, 100)])
    cfg = config(tmp_path, max_pages=2)
    manifest = Collector(cfg, catalog(), client, run_root=tmp_path / "run").collect("run-1")
    assert len(client.calls) == 2
    assert client.calls[1]["search_after"] == ["id-99"]
    assert manifest["partitions"]["2019"]["status"] == "complete"


def test_full_first_page_at_pilot_limit_is_limited(tmp_path):
    client = FakeClient([page(100, 0)])
    manifest = Collector(config(tmp_path, max_pages=1), catalog(), client, run_root=tmp_path / "run").collect("run-1")
    assert manifest["partitions"]["2019"]["status"] == "limited"


def test_restart_uses_existing_cursor_without_duplicate_page(tmp_path):
    run_root = tmp_path / "run"
    first_client = FakeClient([page(100, 0)])
    Collector(config(tmp_path, max_pages=1), catalog(), first_client, run_root=run_root).collect("run-1")
    second_client = FakeClient([page(1, 100)])
    manifest = Collector(config(tmp_path, max_pages=2), catalog(), second_client, run_root=run_root).collect("run-1")
    assert len(second_client.calls) == 1
    assert second_client.calls[0]["search_after"] == ["id-99"]
    assert manifest["partitions"]["2019"]["pages"] == 2


def test_invalid_response_does_not_advance_partition(tmp_path):
    client = FakeClient(error=InvalidResponseError("bad page"))
    manifest = Collector(config(tmp_path), catalog(), client, run_root=tmp_path / "run").collect("run-1")
    partition = manifest["partitions"]["2019"]
    assert partition["status"] == "failed"
    assert partition["pages"] == 0
