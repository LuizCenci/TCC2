import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.metodos.taxas import construir_agg_taxa
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
    inserir_execucao(conn, "T2", utc(2032, 6, 1), [ANO])
    for i in range(3):
        inserir_registro(conn, "T2", f"api2-{i}", ano=ANO, classe=283, orgao=9731,
                         municipio=4106902, ajuizamento=utc(2031, 3, 10, 9), assuntos=(5560,),
                         movimentos=[], numero=f"2{i}")
    executar_transformacoes(conn)
    construir_agg_taxa(conn)
    return conn


def test_agg_taxa_por_tipo_e_serie(base):
    rows = base.execute(
        "SELECT tipo_procedimento, serie, mesorregiao_id, n, pop_feminina, taxa_bruta_100k,"
        " taxa_eb_100k, pergunta FROM gold.agg_taxa WHERE ano_ajuizamento=%s", (ANO,)).fetchall()
    assert rows
    assert {r[7] for r in rows} == {"Q02"}
    estratos = {(r[0], r[1]) for r in rows}
    for t, s in estratos:
        assert sum(1 for r in rows if (r[0], r[1]) == (t, s)) == 10
    assert sum(r[3] for r in rows if r[1] == "ampliada") == 3
    for r in rows:
        if r[3] > 0:
            assert r[5] == pytest.approx(r[3] / r[4] * 1e5)
        assert r[6] is not None


def test_aplicar_esquema_gold_nao_apaga_agregados(base):
    base.execute("INSERT INTO gold.agg_volume (pergunta, ano_ajuizamento, serie, n)"
                 " VALUES ('Q01', 2099, 'sentinela', 7)")
    aplicar_esquema_gold(base)
    aplicar_esquema_gold(base)
    assert base.execute("SELECT n FROM gold.agg_volume WHERE serie='sentinela'").fetchone()[0] == 7
    base.execute("DELETE FROM gold.agg_volume WHERE serie='sentinela'")
