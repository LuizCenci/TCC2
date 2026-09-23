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


def build_pilot_summary(run_root: Path, catalog: Catalog) -> PilotSummary:
    process_ids: set[str] = set()
    nature_process_ids: dict[str, set[str]] = {nature: set() for nature in ("civel", "penal", "infracional")}
    duplicate_ids = 0
    by_year: dict[str, dict[str, Any]] = {}

    for path in sorted(Path(run_root).rglob("*.response.json.gz")):
        year = next((part.split("=", 1)[1] for part in path.parts if part.startswith("year=")), "unknown")
        data = _read(path)
        hits_obj = data.get("hits", {})
        hits = hits_obj.get("hits", [])
        total = hits_obj.get("total", {})
        year_summary = by_year.setdefault(
            year,
            {
                "pages": 0,
                "records": 0,
                "total_value": total.get("value"),
                "total_relation": total.get("relation"),
                "missing_fields": {field: 0 for field in FIELDS},
                "nature_counts": {nature: 0 for nature in nature_process_ids},
            },
        )
        year_summary["pages"] += 1
        year_summary["records"] += len(hits)
        year_summary["total_value"] = total.get("value")
        year_summary["total_relation"] = total.get("relation")
        for hit in hits:
            source = hit.get("_source") or {}
            process_id = str(source.get("id") or hit.get("_id") or "")
            if process_id in process_ids:
                duplicate_ids += 1
            process_ids.add(process_id)
            for field in FIELDS:
                if field not in source or source[field] is None:
                    year_summary["missing_fields"][field] += 1
            codes = {
                int(subject["codigo"])
                for subject in source.get("assuntos", [])
                if isinstance(subject, dict) and subject.get("codigo") is not None
            }
            for nature in catalog.natures_for(codes):
                nature_process_ids[nature].add(process_id)
                year_summary["nature_counts"][nature] += 1

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
            "| Ano | Páginas | Registros | Total informado | Relação |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for year, values in sorted(summary.by_year.items()):
        lines.append(
            f"| {year} | {values['pages']} | {values['records']} | "
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
        ]
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines), encoding="utf-8")
    return destination
