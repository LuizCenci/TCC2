"""Partitioned, resumable orchestration of Bronze collection."""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

from .bronze import ArtifactConflictError, BronzeStore
from .catalog import Catalog
from .client import DatajudClient
from .config import CollectionConfig
from .metadata import ManifestStore
from .query import build_diagnostic_query, build_main_query
from . import __version__

logger = logging.getLogger(__name__)


class Collector:
    def __init__(
        self,
        config: CollectionConfig,
        catalog: Catalog,
        client: DatajudClient,
        *,
        run_root: Path | None = None,
    ) -> None:
        self.config = config
        self.catalog = catalog
        self.client = client
        self.run_root = Path(run_root) if run_root is not None else None

    def collect(
        self,
        run_id: str,
        query_kind: Literal["main", "diagnostic"] = "main",
    ) -> dict:
        if query_kind not in {"main", "diagnostic"}:
            raise ValueError("query_kind deve ser main ou diagnostic")
        if "/" in run_id or "\\" in run_id or not run_id.strip():
            raise ValueError("run_id inválido")
        run_root = self._resolve_run_root(run_id)
        manifest_store = ManifestStore(run_root)
        manifest = manifest_store.load_or_create(
            {
                "run_id": run_id,
                "endpoint": self.config.endpoint,
                "tribunal": self.config.tribunal,
                "grau": self.config.grau,
                "years": list(self.config.years),
                "query_kind": query_kind,
                "catalog_version": self.catalog.version,
                "catalog_source_hash": self.catalog.source_hash,
                "config_hash": self.config.fingerprint(),
                "collector_version": __version__,
                "page_size": self.config.page_size,
                "max_pages_per_partition": self.config.max_pages_per_partition,
                "partitions": {},
            }
        )
        manifest["status"] = "running"
        manifest_store.save(manifest)
        bronze = BronzeStore(run_root)
        builder = build_main_query if query_kind == "main" else build_diagnostic_query
        logger.info(
            "coleta %s: consulta=%s anos=%s páginas/ano<=%d",
            run_id, query_kind, list(self.config.years), self.config.max_pages_per_partition,
        )

        for year in self.config.years:
            partition = manifest.setdefault("partitions", {}).setdefault(
                str(year),
                {
                    "status": "pending",
                    "pages": 0,
                    "records": 0,
                    "artifacts": [],
                },
            )
            partition["year"] = year
            if partition.get("status") == "complete":
                try:
                    self._verify_manifest_artifacts(bronze, partition, run_root)
                    logger.info("ano %d: já concluído, pulando", year)
                    continue
                except ArtifactConflictError as exc:
                    partition["status"] = "failed"
                    partition["error"] = {"type": type(exc).__name__, "message": str(exc)}
                    manifest_store.save(manifest)
                    break
            partition["status"] = "running"
            cursor = partition.get("last_cursor")
            logger.info(
                "ano %d: iniciando%s",
                year,
                f" (retomando após página {partition.get('pages', 0)})" if cursor is not None else "",
            )
            try:
                self._verify_manifest_artifacts(bronze, partition, run_root)
                cursor = self._reconcile_orphans(bronze, partition, year, run_root, cursor)
                manifest_store.save(manifest)
                seen_cursors = {repr(cursor)} if cursor is not None else set()
                while int(partition.get("pages", 0)) < self.config.max_pages_per_partition:
                    body = builder(self.config, self.catalog, year, cursor)
                    page = self.client.search(body)
                    page_number = int(partition.get("pages", 0)) + 1
                    artifact = bronze.write_page(year, page_number, body, page.raw)
                    partition["pages"] = page_number
                    partition["records"] = int(partition.get("records", 0)) + len(page.hits)
                    partition["total"] = page.total
                    logger.info(
                        "ano %d: página %d, %d registros (acumulado %d, total=%s (%s))",
                        year, page_number, len(page.hits), partition["records"],
                        page.total.get("value"), page.total.get("relation"),
                    )
                    partition["last_cursor"] = page.next_cursor
                    partition["response_meta"] = {
                        "took": page.raw.get("took"),
                        "timed_out": page.raw.get("timed_out"),
                        "shards_failed": page.raw.get("_shards", {}).get("failed"),
                    }
                    partition["request_meta"] = getattr(self.client, "last_request_meta", {})
                    partition["artifacts"].append(
                        {
                            "page": page_number,
                            "request": str(artifact.request_path.relative_to(run_root)),
                            "response": str(artifact.response_path.relative_to(run_root)),
                            "sha256": artifact.sha256,
                            "records": len(page.hits),
                        }
                    )
                    manifest_store.save(manifest)
                    if not page.hits or len(page.hits) < self.config.page_size:
                        partition["status"] = "complete"
                        break
                    if page.next_cursor is None:
                        partition["status"] = "complete"
                        break
                    cursor_key = repr(page.next_cursor)
                    if cursor_key in seen_cursors:
                        raise ValueError("cursor search_after repetido")
                    seen_cursors.add(cursor_key)
                    cursor = page.next_cursor
                else:
                    partition["status"] = "limited"
            except Exception as exc:
                partition["status"] = "failed"
                partition["error"] = {"type": type(exc).__name__, "message": str(exc)}
                logger.error("ano %d: falhou: %s: %s", year, type(exc).__name__, exc)
                manifest_store.save(manifest)
                if not self.config.continue_on_partition_error:
                    break
            if partition["status"] != "failed":
                logger.info(
                    "ano %d: %s, %d páginas, %d registros",
                    year, partition["status"], partition.get("pages", 0), partition.get("records", 0),
                )
            manifest_store.save(manifest)

        statuses = [item.get("status") for item in manifest["partitions"].values()]
        if statuses and all(status == "complete" for status in statuses):
            manifest["status"] = "complete"
        elif any(status == "failed" for status in statuses):
            manifest["status"] = "failed"
        else:
            manifest["status"] = "limited"
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        manifest_store.save(manifest)
        return manifest

    def _resolve_run_root(self, run_id: str) -> Path:
        if self.run_root is not None:
            return self.run_root
        base = self.config.output_root / "bronze" / "datajud" / self.config.tribunal.lower()
        matches = sorted(base.glob(f"collected_at=*/run_id={run_id}"))
        if matches:
            return matches[-1]
        return base / f"collected_at={date.today().isoformat()}" / f"run_id={run_id}"

    @staticmethod
    def _verify_manifest_artifacts(bronze: BronzeStore, partition: dict, run_root: Path) -> None:
        for entry in partition.get("artifacts", []):
            response = run_root / entry["response"]
            request = run_root / entry["request"]
            artifact = bronze.artifact_for(partition["year"], int(entry["page"]))
            if artifact is None or artifact.response_path != response or artifact.request_path != request:
                raise ArtifactConflictError("artefato listado no manifesto está ausente")
            bronze.verify_artifact(artifact, entry.get("sha256"))

    def _reconcile_orphans(
        self, bronze: BronzeStore, partition: dict, year: int, run_root: Path, cursor: list | None
    ) -> list | None:
        partition["year"] = year
        known_pages = int(partition.get("pages", 0))
        while True:
            page_number = known_pages + 1
            artifact = bronze.artifact_for(year, page_number)
            if artifact is None:
                break
            bronze.verify_artifact(artifact)
            raw = bronze.read_response(artifact)
            hits = raw.get("hits", {}).get("hits")
            total = raw.get("hits", {}).get("total")
            if not isinstance(hits, list) or not isinstance(total, dict):
                raise ArtifactConflictError("resposta órfã inválida")
            for hit in hits:
                if not isinstance(hit.get("sort"), list) or not hit["sort"]:
                    raise ArtifactConflictError("resposta órfã sem cursor")
            page_cursor = list(hits[-1]["sort"]) if hits else None
            known_pages = page_number
            partition["pages"] = known_pages
            partition["records"] = int(partition.get("records", 0)) + len(hits)
            partition["total"] = total
            partition["last_cursor"] = page_cursor
            partition.setdefault("artifacts", []).append(
                {
                    "page": page_number,
                    "request": str(artifact.request_path.relative_to(run_root)),
                    "response": str(artifact.response_path.relative_to(run_root)),
                    "sha256": artifact.sha256,
                    "records": len(hits),
                }
            )
            cursor = page_cursor
            if not hits or len(hits) < self.config.page_size:
                partition["status"] = "complete"
                break
        return cursor
