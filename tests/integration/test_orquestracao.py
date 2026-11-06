"""Fluxos Prefect com cliente falso: nenhuma chamada à API real."""

import json
from pathlib import Path

import pytest

pytest.importorskip("prefect", reason="extra 'orquestracao' não instalado")
from prefect.testing.utilities import prefect_test_harness  # noqa: E402

from datajud_tcc.client import SearchPage
from datajud_tcc.orquestracao import etapas, fluxos  # noqa: E402

MARCA_INICIAL = "2026-10-05T18:00:31.594Z"


@pytest.fixture(autouse=True, scope="module")
def prefect_local():
    with prefect_test_harness():
        yield


def _pagina(datas, ano=2024):
    hits = [
        {"_id": f"{ano}-{i}", "_source": {"id": f"{ano}-{i}", "dataHoraUltimaAtualizacao": d}, "sort": [f"{ano}-{i}"]}
        for i, d in enumerate(datas)
    ]
    total = {"value": len(hits), "relation": "eq"}
    raw = {
        "took": 1,
        "timed_out": False,
        "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
        "hits": {"total": total, "hits": hits},
    }
    cursor = [hits[-1]["sort"][0]] if hits else None
    return SearchPage(raw=raw, hits=tuple(hits), next_cursor=cursor, total=total)


class ClienteFalso:
    def __init__(self, paginas):
        self.paginas = list(paginas)
        self.consultas = []

    def search(self, body):
        self.consultas.append(body)
        return self.paginas.pop(0)


@pytest.fixture
def ambiente(tmp_path, monkeypatch):
    texto = Path("config/collection.incremental.yaml").read_text(encoding="utf-8")
    config = tmp_path / "incremental.yaml"
    config.write_text(texto.replace("years: [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]", "years: [2024]"), encoding="utf-8")
    monkeypatch.setattr(fluxos, "RAIZ_EXECUCOES", tmp_path / "bronze")
    monkeypatch.setattr(fluxos, "ARQUIVO_MARCA", tmp_path / "estado" / "marca.json")
    monkeypatch.setattr(fluxos, "RETENTATIVAS", 0)
    return config


def _filtros(cliente):
    return cliente.consultas[0]["query"]["bool"]["filter"]


def test_coleta_incremental_usa_marca_inicial_e_avanca_marca(ambiente, monkeypatch):
    cliente = ClienteFalso([_pagina(["2026-11-01T10:00:00.000Z", "2026-11-02T08:30:00.000Z"])])
    monkeypatch.setattr(fluxos, "_cliente", lambda config: cliente)
    resultado = fluxos.coleta_incremental(config_path=str(ambiente), marca_inicial=MARCA_INICIAL)
    assert {"range": {"dataHoraUltimaAtualizacao": {"gt": MARCA_INICIAL}}} in _filtros(cliente)
    assert resultado["status"] == "complete" and resultado["registros"] == 2
    assert resultado["marca_dagua"] == "2026-11-02T08:30:00.000Z"
    manifesto = json.loads(Path(resultado["run_root"], "manifest.json").read_text(encoding="utf-8"))
    assert manifesto["updated_since"] == MARCA_INICIAL


def test_segunda_coleta_parte_da_marca_gravada(ambiente, monkeypatch):
    primeiro = ClienteFalso([_pagina(["2026-11-02T08:30:00.000Z"])])
    monkeypatch.setattr(fluxos, "_cliente", lambda config: primeiro)
    fluxos.coleta_incremental(config_path=str(ambiente), marca_inicial=MARCA_INICIAL)
    segundo = ClienteFalso([_pagina([])])
    monkeypatch.setattr(fluxos, "_cliente", lambda config: segundo)
    resultado = fluxos.coleta_incremental(config_path=str(ambiente))
    assert {"range": {"dataHoraUltimaAtualizacao": {"gt": "2026-11-02T08:30:00.000Z"}}} in _filtros(segundo)
    assert resultado["registros"] == 0 and resultado["marca_dagua"] == "2026-11-02T08:30:00.000Z"


def test_coleta_sem_marca_falha_sem_chamar_api(ambiente, monkeypatch):
    cliente = ClienteFalso([])
    monkeypatch.setattr(fluxos, "_cliente", lambda config: cliente)
    with pytest.raises(ValueError, match="marca"):
        fluxos.coleta_incremental(config_path=str(ambiente))
    assert cliente.consultas == []


def test_pipeline_encadeia_coleta_silver_e_gold(ambiente, monkeypatch):
    monkeypatch.setattr(fluxos, "_cliente", lambda config: ClienteFalso([_pagina(["2026-11-01T10:00:00.000Z"])]))
    chamadas = []
    monkeypatch.setattr(etapas, "carregar_silver", lambda run_root: chamadas.append(("silver", Path(run_root).name)) or {"registros": 1})
    monkeypatch.setattr(etapas, "construir_gold", lambda versao_regras: chamadas.append(("gold", versao_regras)) or {"tabelas": 0})
    resultado = fluxos.pipeline_incremental(config_path=str(ambiente), marca_inicial=MARCA_INICIAL, versao_regras="teste-v1")
    assert [c[0] for c in chamadas] == ["silver", "gold"]
    assert chamadas[1][1] == "teste-v1"
    assert resultado["silver"]["registros"] == 1
    assert resultado["silver"]["segundos"] >= 0


def test_pipeline_nao_carrega_silver_se_coleta_falhar(ambiente, monkeypatch):
    class ClienteQueFalha:
        def search(self, body):
            raise RuntimeError("HTTP 504 simulado")

    monkeypatch.setattr(fluxos, "_cliente", lambda config: ClienteQueFalha())
    chamadas = []
    monkeypatch.setattr(etapas, "carregar_silver", lambda run_root: chamadas.append("silver"))
    with pytest.raises(RuntimeError, match="coleta"):
        fluxos.pipeline_incremental(config_path=str(ambiente), marca_inicial=MARCA_INICIAL, versao_regras="teste-v1")
    assert chamadas == []


def test_etapa_gold_ainda_nao_implementada():
    with pytest.raises(NotImplementedError):
        etapas.construir_gold("v1")


def test_tarefa_silver_devolve_segundos_e_cria_artefato(monkeypatch):
    contagens = {"paginas": 1, "registros": 2, "assuntos": 3, "movimentos": 4, "complementos": 5}
    monkeypatch.setattr(etapas, "carregar_silver", lambda run_root: dict(contagens))
    resultado = fluxos.carga_silver("work/qualquer")
    assert {k: resultado[k] for k in contagens} == contagens
    assert resultado["segundos"] >= 0


def test_prefect_captura_logger_do_pacote():
    from prefect.settings import get_current_settings

    extras = get_current_settings().logging.extra_loggers
    assert "datajud_tcc" in (extras if isinstance(extras, (list, set, tuple)) else str(extras).split(","))
