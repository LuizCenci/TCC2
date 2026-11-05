"""Marca d'água da coleta incremental, baseada em dataHoraUltimaAtualizacao.

O campo registra quando o tribunal reenviou o registro ao Datajud (cargas em lote),
não movimentos processuais. Por isso a marca só avança e cada lote vem inteiro.
"""

from __future__ import annotations

import gzip
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _instante(valor: str) -> datetime:
    instante = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    return instante if instante.tzinfo else instante.replace(tzinfo=timezone.utc)


def maior_atualizacao_da_execucao(run_root: Path) -> str | None:
    """Maior dataHoraUltimaAtualizacao entre as páginas listadas no manifesto."""
    run_root = Path(run_root)
    manifesto = json.loads((run_root / "manifest.json").read_text(encoding="utf-8"))
    maior: tuple[datetime, str] | None = None
    for particao in manifesto.get("partitions", {}).values():
        for artefato in particao.get("artifacts", []):
            resposta = json.loads(gzip.decompress((run_root / artefato["response"]).read_bytes()))
            for hit in resposta.get("hits", {}).get("hits", []):
                valor = (hit.get("_source") or {}).get("dataHoraUltimaAtualizacao")
                if not valor:
                    continue
                instante = _instante(str(valor))
                if maior is None or instante > maior[0]:
                    maior = (instante, str(valor))
    return None if maior is None else maior[1]


class MarcaDagua:
    """Estado persistido em JSON: valor atual e histórico das execuções."""

    def __init__(self, caminho: Path) -> None:
        self.caminho = Path(caminho)

    def _estado(self) -> dict[str, Any]:
        if not self.caminho.exists():
            return {"valor": None, "historico": []}
        return json.loads(self.caminho.read_text(encoding="utf-8"))

    def ler(self) -> str | None:
        return self._estado().get("valor")

    def gravar(self, valor: str, *, run_id: str) -> None:
        estado = self._estado()
        atual = estado.get("valor")
        if atual is not None and _instante(valor) < _instante(atual):
            raise ValueError(f"marca d'água não pode recuar: {atual} -> {valor}")
        estado["valor"] = valor
        estado["historico"].append(
            {"run_id": run_id, "valor": valor, "gravado_em": datetime.now(timezone.utc).isoformat()}
        )
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.caminho.with_name(self.caminho.name + ".tmp")
        temporario.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(self.caminho)
