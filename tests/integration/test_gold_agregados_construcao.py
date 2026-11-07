import pytest

from datajud_tcc.gold import construcao as gold_construcao, referencias
from datajud_tcc.gold.metodos import construcao

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]


def test_construir_agregados_idempotente(conn_banco_modulo):
    conn = conn_banco_modulo
    versao = referencias.ler_regras()["versao_regras"]
    gold_construcao.construir_gold(conn, versao)
    a = construcao.construir_agregados(conn, versao)
    gold_construcao.construir_gold(conn, versao)
    b = construcao.construir_agregados(conn, versao)
    assert a == b
    assert set(a) == set(construcao.TABELAS_AGG)


def test_construir_agregados_versao_divergente(conn_banco_modulo):
    with pytest.raises(ValueError):
        construcao.construir_agregados(conn_banco_modulo, "outra")
