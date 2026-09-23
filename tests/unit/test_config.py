from pathlib import Path

import pytest

from datajud_tcc.config import CollectionConfig


def valid_mapping(tmp_path: Path) -> dict:
    return {
        "endpoint": "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search",
        "tribunal": "TJPR",
        "grau": "G1",
        "years": list(range(2019, 2026)),
        "page_size": 100,
        "max_pages_per_partition": 1,
        "connect_timeout_seconds": 10,
        "read_timeout_seconds": 60,
        "max_attempts": 3,
        "max_wait_seconds": 30,
        "output_root": "work",
        "continue_on_partition_error": False,
    }


def test_pilot_config_has_seven_years_and_one_page(tmp_path):
    cfg = CollectionConfig.from_mapping(valid_mapping(tmp_path))
    assert cfg.years == tuple(range(2019, 2026))
    assert cfg.page_size == 100
    assert cfg.max_pages_per_partition == 1


@pytest.mark.parametrize(
    "patch",
    [
        {"years": [2025, 2019]},
        {"page_size": 9},
        {"page_size": 10001},
        {"output_root": "../outside"},
    ],
)
def test_invalid_collection_config_is_rejected(tmp_path, patch):
    raw = valid_mapping(tmp_path) | patch
    with pytest.raises(ValueError):
        CollectionConfig.from_mapping(raw)
