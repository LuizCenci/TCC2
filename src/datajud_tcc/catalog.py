"""Versioned TPU catalog used by the thematic selection."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any

import yaml


NATURES = frozenset({"civel", "penal", "infracional"})
EXTENSION_TYPES = frozenset({"assunto", "classe"})
EXTENSION_GROUPS = frozenset({"especifica", "ambigua", "secundaria"})


@dataclass(frozen=True)
class CatalogEntry:
    codigo: int
    tipo: str
    descricao: str
    natureza: str
    fonte: str
    consultado_em: str
    vigencia: str | None
    justificativa: str
    grupo: str | None = None


def _entry(item: Any) -> CatalogEntry:
    if not isinstance(item, dict):
        raise ValueError("entrada de catálogo inválida")
    code = int(item["codigo"])
    nature = str(item["natureza"])
    if nature not in NATURES:
        raise ValueError(f"natureza inválida: {nature}")
    required = ("tipo", "descricao", "fonte", "consultado_em", "justificativa")
    if any(not str(item.get(key, "")).strip() for key in required):
        raise ValueError(f"entrada incompleta: {code}")
    grupo = item.get("grupo")
    return CatalogEntry(
        codigo=code,
        tipo=str(item["tipo"]),
        descricao=str(item["descricao"]),
        natureza=nature,
        fonte=str(item["fonte"]),
        consultado_em=str(item["consultado_em"]),
        vigencia=item.get("vigencia"),
        justificativa=str(item["justificativa"]),
        grupo=None if grupo is None else str(grupo),
    )


@dataclass(frozen=True)
class Catalog:
    version: str
    source_hash: str
    entries: tuple[CatalogEntry, ...]
    diagnostic_classes: tuple[int, ...]
    extensions: tuple[CatalogEntry, ...] = ()

    @classmethod
    def load(cls, path: Path) -> "Catalog":
        raw: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("catálogo deve conter um objeto YAML")
        entries_raw = raw.get("assuntos")
        if not isinstance(entries_raw, list) or not entries_raw:
            raise ValueError("catálogo deve conter a lista assuntos")

        entries: list[CatalogEntry] = []
        seen: set[int] = set()
        for item in entries_raw:
            entry = _entry(item)
            if entry.codigo in seen:
                raise ValueError(f"código duplicado: {entry.codigo}")
            entries.append(entry)
            seen.add(entry.codigo)

        # Extensões ampliam o filtro principal além do núcleo; assuntos e classes
        # têm numerações independentes na TPU, por isso a unicidade é por tipo.
        extensions: list[CatalogEntry] = []
        seen_by_type: dict[str, set[int]] = {"assunto": set(seen), "classe": set()}
        for item in raw.get("extensoes") or []:
            entry = _entry(item)
            if entry.tipo not in EXTENSION_TYPES:
                raise ValueError(f"tipo de extensão inválido: {entry.tipo}")
            if entry.grupo not in EXTENSION_GROUPS:
                raise ValueError(f"grupo de extensão inválido: {entry.grupo}")
            if entry.codigo in seen_by_type[entry.tipo]:
                raise ValueError(f"código duplicado: {entry.codigo}")
            extensions.append(entry)
            seen_by_type[entry.tipo].add(entry.codigo)

        diagnostic = raw.get("classes_diagnosticas", [])
        diagnostic_classes = tuple(sorted({int(code) for code in diagnostic}))
        return cls(
            version=str(raw.get("versao", "")).strip(),
            source_hash=hashlib.sha256(path.read_bytes()).hexdigest(),
            entries=tuple(entries),
            diagnostic_classes=diagnostic_classes,
            extensions=tuple(extensions),
        )

    @property
    def subject_codes(self) -> tuple[int, ...]:
        return tuple(entry.codigo for entry in self.entries)

    @property
    def extension_subject_codes(self) -> tuple[int, ...]:
        return tuple(entry.codigo for entry in self.extensions if entry.tipo == "assunto")

    @property
    def extension_class_codes(self) -> tuple[int, ...]:
        return tuple(entry.codigo for entry in self.extensions if entry.tipo == "classe")

    def natures_for(self, codes: set[int]) -> frozenset[str]:
        return frozenset(entry.natureza for entry in self.entries if entry.codigo in codes)

    def entry_for(self, code: int) -> CatalogEntry | None:
        return next((entry for entry in self.entries if entry.codigo == code), None)
