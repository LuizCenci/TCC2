from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_tracked_source_does_not_contain_embedded_api_key():
    candidates = [ROOT / ".env.example"]
    text = "\n".join(
        path.read_text(encoding="utf-8") for path in candidates if path.exists()
    )
    assert 'Authorization": "APIKey ' not in text
    assert "DATAJUD_API_KEY=" in (ROOT / ".env.example").read_text(encoding="utf-8")
