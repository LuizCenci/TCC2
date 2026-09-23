import json

from datajud_tcc.metadata import ManifestStore
import pytest


def test_manifest_is_saved_without_secret(tmp_path):
    store = ManifestStore(tmp_path)
    manifest = store.load_or_create(
        {
            "run_id": "run-1",
            "endpoint": "https://example.test",
            "api_key": "segredo-sintetico",
        }
    )
    store.save(manifest)
    text = (tmp_path / "manifest.json").read_text(encoding="utf-8")
    assert "Authorization" not in text
    assert "APIKey" not in text
    assert "segredo-sintetico" not in text
    assert json.loads(text)["run_id"] == "run-1"


def test_existing_manifest_rejects_changed_collection_context(tmp_path):
    store = ManifestStore(tmp_path)
    context = {
        "run_id": "run-1",
        "endpoint": "https://example.test",
        "tribunal": "TJPR",
        "grau": "G1",
        "query_kind": "main",
        "catalog_source_hash": "catalog-a",
        "config_hash": "config-a",
    }
    store.save(store.load_or_create(context))
    with pytest.raises(ValueError, match="contexto"):
        store.load_or_create(context | {"catalog_source_hash": "catalog-b"})
