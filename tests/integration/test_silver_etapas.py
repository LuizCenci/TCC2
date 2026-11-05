"""Etapa Silver do orquestrador com conexão injetada."""
import pytest
from test_silver_carga import _criar_execucao

from datajud_tcc.orquestracao import etapas
from datajud_tcc.silver.esquema import aplicar_esquema

pytestmark = pytest.mark.banco


def test_etapa_carregar_silver_com_conexao_nao_commita(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path, anos=(2024,))
    r = etapas.carregar_silver(tmp_path, conn=conn_banco)
    assert r["registros"] == 3
    n = conn_banco.execute(
        "SELECT count(*) FROM silver.registro WHERE run_id='run-sint'").fetchone()[0]
    assert n == 3
