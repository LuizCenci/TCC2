"""Aggregate privacy-safe diagnostics from Bronze response pages."""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .catalog import Catalog

FIELDS = ("assuntos", "classe", "dataAjuizamento", "orgaoJulgador", "movimentos")


@dataclass(frozen=True)
class PilotSummary:
    process_count: int
    nature_counts: dict[str, int]
    by_year: dict[str, dict[str, Any]]
    duplicate_ids: int


def _read(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rb") as handle:
        return json.loads(handle.read().decode("utf-8"))


def _empty_year(status: str = "observed") -> dict[str, Any]:
    return {
        "status": status,
        "pages": 0,
        "records": 0,
        "total_value": None,
        "total_relation": None,
        "missing_fields": {field: 0 for field in FIELDS},
        "nature_counts": {nature: 0 for nature in ("civel", "penal", "infracional")},
    }


def build_pilot_summary(run_root: Path, catalog: Catalog) -> PilotSummary:
    run_root = Path(run_root)
    if not run_root.exists():
        raise FileNotFoundError(run_root)
    manifest_path = run_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else None
    if manifest and manifest.get("catalog_source_hash") not in (None, catalog.source_hash):
        raise ValueError("catálogo atual diverge do catálogo registrado no manifesto")

    process_ids: set[str] = set()
    nature_process_ids: dict[str, set[str]] = {nature: set() for nature in ("civel", "penal", "infracional")}
    duplicate_ids = 0
    by_year: dict[str, dict[str, Any]] = {}
    if manifest:
        for year, partition in manifest.get("partitions", {}).items():
            values = _empty_year(str(partition.get("status", "unknown")))
            values["pages"] = partition.get("pages", 0)
            values["records"] = partition.get("records", 0)
            values["total_value"] = (partition.get("total") or {}).get("value")
            values["total_relation"] = (partition.get("total") or {}).get("relation")
            by_year[str(year)] = values

    if manifest:
        response_paths = [
            run_root / item["response"]
            for partition in manifest.get("partitions", {}).values()
            for item in partition.get("artifacts", [])
        ]
    else:
        response_paths = sorted(run_root.rglob("*.response.json.gz"))

    for path in response_paths:
        year = next((part.split("=", 1)[1] for part in path.parts if part.startswith("year=")), "unknown")
        values = by_year.setdefault(year, _empty_year())
        if not path.exists():
            values["missing_artifacts"] = True
            values["status"] = "failed"
            continue
        data = _read(path)
        hits_obj = data.get("hits", {})
        hits = hits_obj.get("hits", [])
        total = hits_obj.get("total", {})
        if not manifest:
            values["pages"] += 1
            values["records"] += len(hits)
        values["total_value"] = total.get("value")
        values["total_relation"] = total.get("relation")
        year_nature_ids: dict[str, set[str]] = {nature: set() for nature in nature_process_ids}
        for hit in hits:
            source = hit.get("_source") or {}
            process_id = str(source.get("numeroProcesso") or source.get("id") or hit.get("_id") or "")
            if process_id in process_ids:
                duplicate_ids += 1
            process_ids.add(process_id)
            for field in FIELDS:
                if field not in source or source[field] is None:
                    values["missing_fields"][field] += 1
            codes = {
                int(subject["codigo"])
                for subject in source.get("assuntos", [])
                if isinstance(subject, dict) and subject.get("codigo") is not None
            }
            for nature in catalog.natures_for(codes):
                nature_process_ids[nature].add(process_id)
                year_nature_ids[nature].add(process_id)
        for nature, ids in year_nature_ids.items():
            values["nature_counts"][nature] += len(ids)

    return PilotSummary(
        process_count=len(process_ids),
        nature_counts={nature: len(ids) for nature, ids in nature_process_ids.items() if ids},
        by_year=by_year,
        duplicate_ids=duplicate_ids,
    )


def write_markdown(summary: PilotSummary, destination: Path) -> Path:
    lines = [
        "# Relatório do piloto Datajud/TJPR",
        "",
        f"Processos únicos observados: **{summary.process_count}**.",
        "",
        "As categorias de natureza podem se sobrepor; suas somas não representam o total de processos.",
        "",
        "## Naturezas derivadas",
        "",
        "| Natureza | Processos únicos |",
        "|---|---:|",
    ]
    for nature, count in sorted(summary.nature_counts.items()):
        lines.append(f"| {nature} | {count} |")
    lines.extend(
        [
            "",
            "## Partições anuais",
            "",
            "| Ano | Estado | Páginas | Registros | Total informado | Relação |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for year, values in sorted(summary.by_year.items()):
        lines.append(
            f"| {year} | {values.get('status')} | {values['pages']} | {values['records']} | "
            f"{values['total_value']} | {values['total_relation']} |"
        )
    lines.extend(
        [
            "",
            f"Duplicações técnicas observadas: **{summary.duplicate_ids}**.",
            "",
            "## Limitações",
            "",
            "- processos não equivalem a vítimas ou ocorrências;",
            "- o município do órgão julgador não representa necessariamente o local do fato;",
            "- `gte` no total da API é limite inferior, não total exato;",
            "- ausência de campo ou movimento não comprova ausência do fato ou do evento judicial.",
            "",
            "## Qualidade estrutural",
            "",
            "| Ano | Campos ausentes |",
            "|---|---|",
        ]
    )
    for year, values in sorted(summary.by_year.items()):
        missing = ", ".join(f"{key}={value}" for key, value in values.get("missing_fields", {}).items())
        lines.append(f"| {year} | {missing} |")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination
