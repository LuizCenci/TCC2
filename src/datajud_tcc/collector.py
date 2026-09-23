"""Partitioned, resumable orchestration of Bronze collection."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

from .bronze import BronzeStore
from .catalog import Catalog
from .client import DatajudClient
from .config import CollectionConfig
from .metadata import ManifestStore
from .query import build_diagnostic_query, build_main_query


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
        run_root = self.run_root or (
            self.config.output_root
            / "bronze"
            / "datajud"
            / self.config.tribunal.lower()
            / f"collected_at={date.today().isoformat()}"
            / f"run_id={run_id}"
        )
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
                "page_size": self.config.page_size,
                "max_pages_per_partition": self.config.max_pages_per_partition,
                "partitions": {},
            }
        )
        manifest["status"] = "running"
        manifest_store.save(manifest)
        bronze = BronzeStore(run_root)
        builder = build_main_query if query_kind == "main" else build_diagnostic_query

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
            if partition.get("status") == "complete":
                continue
            partition["status"] = "running"
            cursor = partition.get("last_cursor")
            try:
                while int(partition.get("pages", 0)) < self.config.max_pages_per_partition:
                    body = builder(self.config, self.catalog, year, cursor)
                    page = self.client.search(body)
                    page_number = int(partition.get("pages", 0)) + 1
                    artifact = bronze.write_page(year, page_number, body, page.raw)
                    partition["pages"] = page_number
                    partition["records"] = int(partition.get("records", 0)) + len(page.hits)
                    partition["total"] = page.total
                    partition["last_cursor"] = page.next_cursor
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
                    cursor = page.next_cursor
                else:
                    partition["status"] = "limited"
            except Exception as exc:
                partition["status"] = "failed"
                partition["error"] = {"type": type(exc).__name__, "message": str(exc)}
                manifest_store.save(manifest)
                if not self.config.continue_on_partition_error:
                    break
            manifest_store.save(manifest)

        statuses = [item.get("status") for item in manifest["partitions"].values()]
        if statuses and all(status == "complete" for status in statuses):
            manifest["status"] = "complete"
        elif any(status == "failed" for status in statuses):
            manifest["status"] = "failed"
        else:
            manifest["status"] = "limited"
        manifest_store.save(manifest)
        return manifest
