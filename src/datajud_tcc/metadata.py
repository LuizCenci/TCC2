"""Run manifest persistence and secret sanitization."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4


SENSITIVE_KEYS = {"api_key", "authorization", "Authorization", "APIKey"}


def _sanitize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): _sanitize(item)
            for key, item in value.items()
            if str(key) not in SENSITIVE_KEYS
        }
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    return value


class ManifestStore:
    def __init__(self, run_root: Path) -> None:
        self.run_root = Path(run_root)
        self.path = self.run_root / "manifest.json"

    def load_or_create(self, context: Mapping[str, Any]) -> dict[str, Any]:
        if self.path.exists():
            manifest = json.loads(self.path.read_text(encoding="utf-8"))
            immutable = (
                "endpoint",
                "tribunal",
                "grau",
                "years",
                "query_kind",
                "catalog_version",
                "catalog_source_hash",
                "config_hash",
                "page_size",
            )
            for key in immutable:
                if key in context and manifest.get(key) != context[key]:
                    raise ValueError(f"contexto imutável divergente no manifesto: {key}")
            return manifest
        manifest = _sanitize(dict(context))
        manifest.setdefault("run_id", uuid4().hex)
        manifest.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        manifest.setdefault("status", "created")
        manifest.setdefault("partitions", {})
        return manifest

    def save(self, manifest: Mapping[str, Any]) -> None:
        payload = _sanitize(dict(manifest))
        self.run_root.mkdir(parents=True, exist_ok=True)
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")
        temporary = self.path.with_name(".manifest.json.tmp")
        temporary.write_bytes(data)
        temporary.replace(self.path)
