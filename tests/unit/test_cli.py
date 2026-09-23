from pathlib import Path

from datajud_tcc import cli


def test_collect_refuses_missing_api_key(monkeypatch, capsys):
    monkeypatch.delenv("DATAJUD_API_KEY", raising=False)
    assert cli.main(["collect", "--config", "config/collection.example.yaml"]) == 2
    assert "DATAJUD_API_KEY" in capsys.readouterr().err


def test_collect_never_prints_key(monkeypatch, capsys):
    secret = "segredo-sintetico"
    monkeypatch.setenv("DATAJUD_API_KEY", secret)

    class FakeCollector:
        def __init__(self, *args, **kwargs):
            pass

        def collect(self, run_id, query_kind):
            return {"run_id": run_id, "status": "limited"}

    monkeypatch.setattr(cli, "Collector", FakeCollector)
    assert cli.main(["collect", "--config", "config/collection.example.yaml"]) == 0
    assert secret not in capsys.readouterr().out
