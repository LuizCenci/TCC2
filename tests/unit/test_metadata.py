import json

from datajud_tcc.metadata import ManifestStore


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
