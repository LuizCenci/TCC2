from pathlib import Path

from datajud_tcc import cli
from datajud_tcc.bronze import BronzeStore


def test_collect_refuses_missing_api_key(monkeypatch, capsys):
    monkeypatch.delenv("DATAJUD_API_KEY", raising=False)
    monkeypatch.setattr(cli, "_load_dotenv", lambda: None)
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


def test_report_command_writes_requested_output(tmp_path):
    response = {
        "hits": {
            "total": {"value": 0, "relation": "eq"},
            "hits": [],
        }
    }
    BronzeStore(tmp_path).write_page(2019, 1, {"size": 100}, response)
    output = tmp_path / "report.md"
    assert cli.main(["report", "--run-root", str(tmp_path), "--output", str(output)]) == 0
    assert output.exists()
