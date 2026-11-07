import time
from datetime import datetime

import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.metodos.sobrevivencia import construir_agg_desfecho
from datajud_tcc.gold.referencias import carregar_referencias
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]
ANO_AP, ANO_MPU = 2033, 2034


@pytest.fixture(scope="module")
def base(conn_banco_modulo):
    conn = conn_banco_modulo
    aplicar_esquema(conn)
    aplicar_esquema_gold(conn)
    carregar_territorio(conn)
    carregar_referencias(conn)
    inserir_execucao(conn, "T10", utc(2036, 6, 1), [ANO_AP, ANO_MPU])
    for i in range(40):
        inserir_registro(conn, "T10", f"ap10-{i}", ano=ANO_AP, classe=282, orgao=1,
                         municipio=4106902, ajuizamento=datetime(2033, 3, 10, 9),
                         assuntos=(10949,), numero=f"10{i:02d}")
    for i in range(40):
        inserir_registro(conn, "T10", f"mp10-{i}", ano=ANO_MPU, classe=1268, orgao=1,
                         municipio=4106902, ajuizamento=datetime(2034, 3, 10, 9),
                         assuntos=(10949,), numero=f"11{i:02d}")
    executar_transformacoes(conn)
    conn.execute(
        "UPDATE gold.fato_processo SET desfecho='EM_ANDAMENTO', censurado=true, reativado=false,"
        " duracao_dias=500 WHERE ano_ajuizamento IN (%s,%s)", (ANO_AP, ANO_MPU))
    ids = [r[0] for r in conn.execute(
        "SELECT registro_id FROM gold.fato_processo WHERE ano_ajuizamento=%s"
        " AND tipo_procedimento='ACAO_PENAL' ORDER BY registro_id", (ANO_AP,)).fetchall()]
    for j, rid in enumerate(ids[:30]):
        des = "CONDENACAO" if j < 20 else "ABSOLVICAO"
        conn.execute("UPDATE gold.fato_processo SET desfecho=%s, censurado=false, duracao_dias=%s,"
                     " reativado=%s WHERE registro_id=%s", (des, 100 + j, j == 0, rid))
    for (rid,) in conn.execute(
            "SELECT registro_id FROM gold.fato_processo WHERE ano_ajuizamento=%s",
            (ANO_MPU,)).fetchall()[:5]:
        conn.execute("UPDATE gold.fato_processo SET desfecho='CONDENACAO', censurado=false"
                     " WHERE registro_id=%s", (rid,))
    t0 = time.time()
    n = construir_agg_desfecho(conn)
    print(f"construir_agg_desfecho: {n} linhas em {time.time() - t0:.1f}s")
    return conn


def _cond(c, variante):
    return c.execute(
        "SELECT n_desfecho, n FROM gold.agg_desfecho WHERE tipo_procedimento='ACAO_PENAL'"
        " AND serie='ampliada' AND estrato='total' AND desfecho='CONDENACAO' AND variante=%s",
        (variante,)).fetchone()


def test_agg_desfecho_variantes_reativado(base):
    esperado = base.execute(
        "SELECT count(*) FILTER (WHERE desfecho='CONDENACAO'), count(*) FROM gold.fato_processo"
        " WHERE tipo_procedimento='ACAO_PENAL' AND reativado AND duracao_dias >= 0").fetchone()
    p, c = _cond(base, "principal"), _cond(base, "com_reativados")
    assert esperado[1] >= 1 and esperado[0] >= 1  # o reativado sintético existe
    assert c[0] - p[0] == esperado[0]
    assert c[1] - p[1] == esperado[1]


def test_agg_desfecho_exclui_mpu(base):
    assert base.execute(
        "SELECT count(*) FROM gold.agg_desfecho WHERE tipo_procedimento NOT IN"
        " ('ACAO_PENAL','INQUERITO')").fetchone()[0] == 0


def test_agg_desfecho_estrato_pequeno_nao_estimavel(base):
    assert base.execute(
        "SELECT count(*) FROM gold.agg_desfecho WHERE (n < 30) <> (NOT estimavel)").fetchone()[0] == 0
    assert base.execute(
        "SELECT count(*) FROM gold.agg_desfecho WHERE n < 30 AND (ia_365 IS NOT NULL OR"
        " ia_730 IS NOT NULL OR ia_1095 IS NOT NULL OR ia_1825 IS NOT NULL)").fetchone()[0] == 0
