import pytest

from datajud_tcc.config import CollectionConfig

from .test_config import valid_mapping


def test_updated_since_is_optional_and_keeps_fingerprint(tmp_path):
    base = CollectionConfig.from_mapping(valid_mapping(tmp_path))
    assert base.updated_since is None
    mapping = valid_mapping(tmp_path) | {"updated_since": "2026-10-05T18:00:31.594Z"}
    incremental = CollectionConfig.from_mapping(mapping)
    assert incremental.updated_since == "2026-10-05T18:00:31.594Z"
    assert incremental.fingerprint() != base.fingerprint()
    assert CollectionConfig.from_mapping(valid_mapping(tmp_path)).fingerprint() == base.fingerprint()


@pytest.mark.parametrize("invalid", ["20261005180031", "ontem", ""])
def test_updated_since_must_be_iso_8601(tmp_path, invalid):
    with pytest.raises(ValueError, match="updated_since"):
        CollectionConfig.from_mapping(valid_mapping(tmp_path) | {"updated_since": invalid})


def test_incremental_config_file_is_valid():
    from pathlib import Path

    config = CollectionConfig.from_yaml(Path("config/collection.incremental.yaml"))
    assert config.years[0] == 2019 and config.grau == "G1"
    assert config.updated_since is None
