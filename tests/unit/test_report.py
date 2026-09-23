import gzip
import json
from pathlib import Path

from datajud_tcc.bronze import BronzeStore
from datajud_tcc.catalog import Catalog
from datajud_tcc.report import build_pilot_summary, write_markdown


def catalog():
    return Catalog.load(Path("config/catalogs/pvd_cnj_2025-07-17.yaml"))


def response(hits, total_relation="eq"):
    return {
        "took": 1,
        "timed_out": False,
        "_shards": {"failed": 0},
        "hits": {
            "total": {"value": len(hits), "relation": total_relation},
            "hits": hits,
        },
    }


def hit(process_id, subjects=None, **source):
    source = {"id": process_id, "dataAjuizamento": "2019-01-01", **source}
    if subjects is not None:
        source["assuntos"] = subjects
    return {"_id": process_id, "_source": source, "sort": [process_id]}


def write_response(run_root, body):
    BronzeStore(run_root).write_page(2019, 1, {"size": 100}, body)


def test_summary_counts_unique_processes_and_multilabel_natures(tmp_path):
    write_response(
        tmp_path,
        response(
            [
                hit("p1", [{"codigo": 10948}, {"codigo": 10949}], movimentos=[]),
                hit("p2", [{"codigo": 10949}], movimentos=[]),
            ]
        ),
    )
    summary = build_pilot_summary(tmp_path, catalog())
    assert summary.process_count == 2
    assert summary.nature_counts == {"civel": 1, "penal": 2}


def test_markdown_excludes_identifiers_and_includes_limitations(tmp_path):
    write_response(tmp_path, response([hit("12345678901234567890", [{"codigo": 10949}])]))
    destination = tmp_path / "report.md"
    write_markdown(build_pilot_summary(tmp_path, catalog()), destination)
    text = destination.read_text(encoding="utf-8")
    assert "12345678901234567890" not in text
    assert "processos não equivalem a vítimas ou ocorrências" in text
    assert "município do órgão julgador não representa necessariamente o local do fato" in text


def test_missing_fields_are_reported_and_gte_is_preserved(tmp_path):
    write_response(tmp_path, response([hit("p1")], total_relation="gte"))
    summary = build_pilot_summary(tmp_path, catalog())
    year = summary.by_year["2019"]
    assert year["total_relation"] == "gte"
    assert year["missing_fields"]["movimentos"] == 1
    assert year["missing_fields"]["orgaoJulgador"] == 1


def test_process_number_is_preferred_for_unique_counts(tmp_path):
    write_response(
        tmp_path,
        response(
            [
                hit("record-a", [{"codigo": 10949}], numeroProcesso="0001"),
                hit("record-b", [{"codigo": 10949}], numeroProcesso="0001"),
            ]
        ),
    )
    summary = build_pilot_summary(tmp_path, catalog())
    assert summary.process_count == 1
    assert summary.nature_counts == {"penal": 1}


def test_report_includes_manifest_failures_and_missing_fields(tmp_path):
    (tmp_path / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": "run-1",
                "status": "failed",
                "catalog_source_hash": catalog().source_hash,
                "partitions": {
                    "2019": {"status": "failed", "pages": 0, "records": 0},
                    "2020": {"status": "complete", "pages": 0, "records": 0},
                },
            }
        ),
        encoding="utf-8",
    )
    summary = build_pilot_summary(tmp_path, catalog())
    assert summary.by_year["2019"]["status"] == "failed"
    assert summary.by_year["2020"]["status"] == "complete"
