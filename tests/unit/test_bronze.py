from pathlib import Path

import pytest

from datajud_tcc.bronze import ArtifactConflictError, BronzeStore


def test_page_round_trip_is_compressed_and_hashed(tmp_path):
    response = {"hits": {"hits": [], "total": {"value": 0, "relation": "eq"}}}
    artifact = BronzeStore(tmp_path).write_page(2019, 1, {"size": 100}, response)
    assert artifact.response_path.suffix == ".gz"
    assert len(artifact.sha256) == 64
    assert BronzeStore(tmp_path).read_response(artifact) == response


def test_rewriting_page_with_different_content_raises_conflict(tmp_path):
    store = BronzeStore(tmp_path)
    store.write_page(2019, 1, {"size": 100}, {"value": 1})
    with pytest.raises(ArtifactConflictError):
        store.write_page(2019, 1, {"size": 100}, {"value": 2})
