import time
from datetime import datetime

import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.metodos.sobrevivencia import construir_agg_tempo
from datajud_tcc.gold.referencias import carregar_referencias
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]
ANO = 2031


@pytest.fixture(scope="module")
def base(conn_banco_modulo):
    conn = conn_banco_modulo
    aplicar_esquema(conn)
    aplicar_esquema_gold(conn)
    carregar_territorio(conn)
    carregar_referencias(conn)
    inserir_execucao(conn, "T3", utc(2032, 6, 1), [ANO])
    aj = datetime(2031, 3, 10, 9)
    for i in range(30):
        mov = [(11423, datetime(2031, 3, 12, 12))] if i < 20 else []
        inserir_registro(conn, "T3", f"api3-{i}", ano=ANO, classe=1268, orgao=1,
                         municipio=4106902, ajuizamento=aj, assuntos=(10949,),
                         movimentos=mov, numero=f"3{i:02d}")
    executar_transformacoes(conn)
    t0 = time.time()
    n = construir_agg_tempo(conn)
    print(f"construir_agg_tempo: {n} linhas em {time.time() - t0:.1f}s")
    return conn


def test_agg_tempo_mpu_censura_na_data_corte(base):
    r = base.execute(
        "SELECT n, n_eventos, estimavel, pct_evento_ate_2, pct_evento_ate_30 FROM gold.agg_tempo"
        " WHERE pergunta='Q05' AND tipo_procedimento='MPU' AND estrato='ano_ajuizamento'"
        " AND valor_estrato=%s AND serie='ampliada'", (str(ANO),)).fetchone()
    assert r is not None
    assert r[0] == 30 and r[1] == 20 and r[2] is True
    assert r[3] == pytest.approx(66.6667, abs=0.01)
    assert r[4] == pytest.approx(66.6667, abs=0.01)
