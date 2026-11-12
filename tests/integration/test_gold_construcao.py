from datetime import datetime

import pytest

from datajud_tcc.gold.construcao import construir_gold
from datajud_tcc.orquestracao import etapas
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = pytest.mark.banco

VERSAO = "gold-2026-11-11"
AJ = datetime(2026, 3, 10, 9, 0, 0)


def _semear(conn):
    aplicar_esquema(conn)
    inserir_execucao(conn, "T6", utc(2030, 7, 1), [2026])
    inserir_registro(conn, "T6", "api-6", ano=2026, classe=1268, orgao=1, municipio=4106902,
                     ajuizamento=AJ, assuntos=(10949,),
                     movimentos=[(11423, utc(2026, 3, 12))], numero="T6-A")


def test_versao_divergente_rejeitada(conn_banco):
    with pytest.raises(ValueError):
        construir_gold(conn_banco, "outra-versao")


@pytest.mark.gold_lento
def test_construcao_idempotente(conn_banco):
    _semear(conn_banco)
    a = construir_gold(conn_banco, VERSAO)
    b = construir_gold(conn_banco, VERSAO)
    assert a == b
    assert a["processos"] >= 1


@pytest.mark.gold_lento
def test_etapa_construir_gold_com_conexao_nao_commita(conn_banco, monkeypatch):
    _semear(conn_banco)
    commits = []
    monkeypatch.setattr(conn_banco, "commit", lambda: commits.append(1))
    r = etapas.construir_gold(VERSAO, conn=conn_banco)
    assert r["versao_regras"] == VERSAO
    assert commits == []
