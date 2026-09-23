"""Immutable persistence for raw Datajud request/response pages."""

from __future__ import annotations

import gzip
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ArtifactConflictError(RuntimeError):
    """A confirmed page path already contains different content."""


@dataclass(frozen=True)
class PageArtifact:
    year: int
    page_number: int
    request_path: Path
    response_path: Path
    sha256: str


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


class BronzeStore:
    def __init__(self, run_root: Path) -> None:
        self.run_root = Path(run_root)

    def write_page(
        self,
        year: int,
        page_number: int,
        request_body: dict[str, Any],
        response_body: dict[str, Any],
    ) -> PageArtifact:
        request_dir = self.run_root / "requests" / f"year={year}"
        response_dir = self.run_root / "responses" / f"year={year}"
        request_path = request_dir / f"page={page_number:06d}.request.json"
        response_path = response_dir / f"page={page_number:06d}.response.json.gz"
        request_bytes = _json_bytes(request_body)
        response_bytes = _json_bytes(response_body)
        compressed = gzip.compress(response_bytes, mtime=0)
        digest = hashlib.sha256(compressed).hexdigest()

        self._write_or_compare(request_path, request_bytes)
        self._write_or_compare(response_path, compressed)
        return PageArtifact(year, page_number, request_path, response_path, digest)

    def read_response(self, artifact: PageArtifact) -> dict[str, Any]:
        with gzip.open(artifact.response_path, "rb") as handle:
            return json.loads(handle.read().decode("utf-8"))

    @staticmethod
    def _write_or_compare(path: Path, content: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if path.read_bytes() != content:
                raise ArtifactConflictError(f"artefato divergente: {path}")
            return
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_bytes(content)
        temporary.replace(path)
