"""Fluxos Prefect: coleta incremental → Silver → Gold (base operacional).

As execuções vão para uma pasta própria da Bronze e ficam fora da base do artigo,
que é congelada (docs/artigo/15-orquestracao-prefect.md). A lógica fica no pacote;
os fluxos só a encadeiam, registram e tratam falhas.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact
from prefect.cache_policies import NO_CACHE
from prefect.logging import get_run_logger

from ..catalog import Catalog
from ..cli import _load_dotenv
from ..client import DatajudClient
from ..collector import Collector
from ..config import CollectionConfig
from . import etapas
from .marca_dagua import MarcaDagua, maior_atualizacao_da_execucao

RAIZ_EXECUCOES = Path("work/bronze/datajud/tjpr/incremental")
ARQUIVO_MARCA = Path("work/estado/marca_dagua_tjpr.json")
CATALOGO = Path("config/catalogs/tjpr_vcm_2026-10-18.yaml")
# Uma nova tentativa da partição inteira, retomando do checkpoint, depois de 10 min.
# Soma-se às tentativas do cliente, por isso é única e espaçada (CLAUDE.md §8).
RETENTATIVAS = 1
ESPERA_RETENTATIVA_S = 600


def _cliente(config: CollectionConfig) -> DatajudClient:
    _load_dotenv()
    chave = os.getenv("DATAJUD_API_KEY", "")
    if not chave.strip():
        raise RuntimeError("DATAJUD_API_KEY não foi informado no ambiente")
    return DatajudClient(
        endpoint=config.endpoint,
        api_key=chave,
        connect_timeout_seconds=config.connect_timeout_seconds,
        read_timeout_seconds=config.read_timeout_seconds,
        max_attempts=config.max_attempts,
        max_wait_seconds=config.max_wait_seconds,
    )


def _config_incremental(config_path: str, marca: str) -> CollectionConfig:
    bruto = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    if not isinstance(bruto, dict):
        raise ValueError("arquivo de configuração deve conter um objeto YAML")
    return CollectionConfig.from_mapping(bruto | {"updated_since": marca})


@task(name="coletar-bronze", tags=["datajud-api"], cache_policy=NO_CACHE)
def coletar(config: CollectionConfig, catalogo: str, run_id: str, run_root: str) -> dict[str, Any]:
    coletor = Collector(config, Catalog.load(Path(catalogo)), _cliente(config), run_root=Path(run_root))
    manifesto = coletor.collect(run_id)
    if manifesto.get("status") != "complete":
        erros = {ano: p.get("error") for ano, p in manifesto.get("partitions", {}).items() if p.get("error")}
        raise RuntimeError(f"coleta incremental terminou com status {manifesto.get('status')}: {erros}")
    return manifesto


@task(name="verificar-completude", cache_policy=NO_CACHE)
def verificar(manifesto: dict[str, Any]) -> int:
    registros = 0
    for ano, particao in manifesto.get("partitions", {}).items():
        total = (particao.get("total") or {}).get("value")
        if total is not None and total != particao.get("records"):
            raise RuntimeError(f"ano {ano}: {particao.get('records')} registros coletados de {total}")
        registros += int(particao.get("records", 0))
    return registros


@flow(name="coleta-incremental")
def coleta_incremental(config_path: str = "config/collection.incremental.yaml", marca_inicial: str | None = None,
                       catalogo: str = str(CATALOGO)) -> dict[str, Any]:
    log = get_run_logger()
    estado = MarcaDagua(ARQUIVO_MARCA)
    marca = estado.ler() or marca_inicial
    if marca is None:
        raise ValueError("sem marca d'água: informe marca_inicial na primeira execução")
    config = _config_incremental(config_path, marca)
    run_id = f"incremental-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:6]}"
    run_root = RAIZ_EXECUCOES / f"run_id={run_id}"
    log.info("coleta %s a partir da marca %s", run_id, marca)
    manifesto = coletar.with_options(retries=RETENTATIVAS, retry_delay_seconds=ESPERA_RETENTATIVA_S)(
        config, catalogo, run_id, str(run_root)
    )
    registros = verificar(manifesto)
    nova = maior_atualizacao_da_execucao(run_root) or marca
    estado.gravar(nova, run_id=run_id)
    resultado = {"run_id": run_id, "run_root": str(run_root), "status": manifesto["status"],
                 "registros": registros, "marca_anterior": marca, "marca_dagua": nova}
    create_markdown_artifact(
        key="coleta-incremental",
        description="Resumo da coleta incremental (base operacional, fora da análise)",
        markdown="\n".join(f"- **{k}**: `{v}`" for k, v in resultado.items()),
    )
    return resultado


@task(name="carregar-silver", cache_policy=NO_CACHE)
def _tarefa_silver(run_root: str) -> dict[str, Any]:
    log = get_run_logger()
    inicio = time.perf_counter()
    contagens = dict(etapas.carregar_silver(Path(run_root)))
    segundos = round(time.perf_counter() - inicio, 3)
    log.info("Silver carregada: %s em %.1f s", contagens, segundos)
    linhas = [f"- **run_root**: `{run_root}`"] + [f"- **{k}**: `{v}`" for k, v in contagens.items()]
    linhas.append(f"- **segundos**: `{segundos}`")
    create_markdown_artifact(key="carga-silver", description="Resumo da carga na Silver",
                             markdown="\n".join(linhas))
    return contagens | {"segundos": segundos}


@task(name="construir-gold", cache_policy=NO_CACHE)
def _tarefa_gold(versao_regras: str) -> dict[str, Any]:
    return etapas.construir_gold(versao_regras)


@flow(name="carga-silver")
def carga_silver(run_root: str) -> dict[str, Any]:
    return _tarefa_silver(run_root)


@flow(name="construcao-gold")
def construcao_gold(versao_regras: str) -> dict[str, Any]:
    return _tarefa_gold(versao_regras)


@flow(name="pipeline-incremental")
def pipeline_incremental(versao_regras: str, config_path: str = "config/collection.incremental.yaml",
                         marca_inicial: str | None = None) -> dict[str, Any]:
    """Coleta → Silver → Gold. Se a coleta falhar, nada é carregado."""
    coleta = coleta_incremental(config_path=config_path, marca_inicial=marca_inicial)
    silver = carga_silver(coleta["run_root"])
    if int(silver.get("registros", 0)) == 0:
        gold = {"pulada": True, "motivo": "nenhum registro novo na Silver"}
        get_run_logger().info("Gold pulada: %s", gold["motivo"])
    else:
        gold = construcao_gold(versao_regras)
    return {"coleta": coleta, "silver": silver, "gold": gold}
