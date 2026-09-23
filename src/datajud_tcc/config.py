"""Configuration models and validation for the Bronze collector."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml
import hashlib
import json


DEFAULT_ENDPOINT = (
    "https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search"
)


@dataclass(frozen=True)
class CollectionConfig:
    endpoint: str
    tribunal: str
    grau: str
    years: tuple[int, ...]
    page_size: int
    max_pages_per_partition: int
    connect_timeout_seconds: float
    read_timeout_seconds: float
    max_attempts: int
    max_wait_seconds: float
    output_root: Path
    continue_on_partition_error: bool = False

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CollectionConfig":
        required = {
            "endpoint",
            "tribunal",
            "grau",
            "years",
            "page_size",
            "max_pages_per_partition",
            "connect_timeout_seconds",
            "read_timeout_seconds",
            "max_attempts",
            "max_wait_seconds",
            "output_root",
        }
        missing = sorted(required - raw.keys())
        if missing:
            raise ValueError(f"configuração sem campos: {', '.join(missing)}")

        years = tuple(int(year) for year in raw["years"])
        if not years or tuple(sorted(set(years))) != years:
            raise ValueError("years deve ser uma sequência crescente sem duplicatas")
        if any(year < 2000 or year > 2100 for year in years):
            raise ValueError("years contém ano fora do intervalo permitido")

        page_size = int(raw["page_size"])
        if not 10 <= page_size <= 10_000:
            raise ValueError("page_size deve estar entre 10 e 10000")

        max_pages = int(raw["max_pages_per_partition"])
        if max_pages < 1:
            raise ValueError("max_pages_per_partition deve ser positivo")

        output_root = Path(str(raw["output_root"]))
        if output_root.is_absolute() or ".." in output_root.parts:
            raise ValueError("output_root deve ser relativo e não conter '..'")

        def positive_float(name: str) -> float:
            value = float(raw[name])
            if value <= 0:
                raise ValueError(f"{name} deve ser positivo")
            return value

        def positive_int(name: str) -> int:
            value = int(raw[name])
            if value < 1:
                raise ValueError(f"{name} deve ser positivo")
            return value

        endpoint = str(raw["endpoint"]).strip()
        if endpoint != DEFAULT_ENDPOINT:
            raise ValueError("endpoint deve ser o endpoint público do TJPR")
        if str(raw["tribunal"]).strip() != "TJPR":
            raise ValueError("tribunal do piloto deve ser TJPR")
        if str(raw["grau"]).strip() != "G1":
            raise ValueError("grau do piloto deve ser G1")
        if output_root != Path("work"):
            raise ValueError("output_root do piloto deve ser work")

        return cls(
            endpoint=endpoint,
            tribunal=str(raw["tribunal"]).strip(),
            grau=str(raw["grau"]).strip(),
            years=years,
            page_size=page_size,
            max_pages_per_partition=max_pages,
            connect_timeout_seconds=positive_float("connect_timeout_seconds"),
            read_timeout_seconds=positive_float("read_timeout_seconds"),
            max_attempts=positive_int("max_attempts"),
            max_wait_seconds=positive_float("max_wait_seconds"),
            output_root=output_root,
            continue_on_partition_error=bool(raw.get("continue_on_partition_error", False)),
        )

    @classmethod
    def from_yaml(cls, path: Path) -> "CollectionConfig":
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("arquivo de configuração deve conter um objeto YAML")
        return cls.from_mapping(raw)

    def fingerprint(self) -> str:
        payload = {
            "endpoint": self.endpoint,
            "tribunal": self.tribunal,
            "grau": self.grau,
            "years": self.years,
            "page_size": self.page_size,
            "connect_timeout_seconds": self.connect_timeout_seconds,
            "read_timeout_seconds": self.read_timeout_seconds,
            "max_attempts": self.max_attempts,
            "max_wait_seconds": self.max_wait_seconds,
            "continue_on_partition_error": self.continue_on_partition_error,
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True, default=list).encode()).hexdigest()
