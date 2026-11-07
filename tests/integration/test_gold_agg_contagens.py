from datetime import datetime

import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.referencias import carregar_referencias, ler_csv, validar
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]

AJ = datetime(2031, 3, 10, 9, 0, 0)
ANO = 2031
MED = "Proibição de contato com a ofendida"

# nome: (classe, assuntos, movimentos)
CENARIOS = {
    "V1": (283, (5560,), []),
    "V2": (283, (12194,), []),
    "V3": (283, (12091,), [(175, utc(2031, 3, 11)), (12140, utc(2031, 3, 12)),
                           (818, utc(2031, 3, 13))]),
    "V4": (261, (10949,), []),
    "M1": (1268, (10949,), [(11423, utc(2031, 3, 12))]),
    "M2": (1268, (10949,), [(11424, utc(2031, 3, 12))]),
    "M3": (1268, (10949,), [(11425, utc(2031, 3, 12))]),
    "M4": (1268, (10949,), [(11423, utc(2031, 3, 12)), (11426, utc(2031, 4, 1))]),
}


@pytest.fixture(scope="module")
def base(conn_banco_modulo):
    conn = conn_banco_modulo
    aplicar_esquema(conn)
    aplicar_esquema_gold(conn)
    carregar_territorio(conn)
    carregar_referencias(conn)
    conn.execute("INSERT INTO ref.cnj_casos_novos VALUES (%s, 1000, 10, 100, 'teste')", (ANO,))
    inserir_execucao(conn, "T5", utc(2032, 6, 1), [ANO])
    ids = {n: inserir_registro(conn, "T5", f"api5-{n}", ano=ANO, classe=c, orgao=9731,
                               municipio=4106902, ajuizamento=AJ, assuntos=a, movimentos=m,
                               numero=f"5{n}")
           for n, (c, a, m) in CENARIOS.items()}
    for n in ("M1", "M4"):
        mid = conn.execute(
            "SELECT movimento_id FROM silver.movimento WHERE registro_id=%s AND codigo=11423",
            (ids[n],)).fetchone()[0]
        conn.execute(
            "INSERT INTO silver.complemento_movimento (movimento_id, ordem, codigo, descricao,"
            " valor, nome) VALUES (%s,1,32,'tipo_de_medida_protetiva',130,%s)", (mid, MED))
    executar_transformacoes(conn)
    return conn


def um(conn, sql, *p):
    return conn.execute(sql, p).fetchone()


def test_referencia_cnj_valida():
    validar()
    linhas = {l["ano"]: l for l in ler_csv("ref_cnj_casos_novos.csv")}
    assert (linhas["2019"]["vd_novos"], linhas["2019"]["feminicidio_novos"],
            linhas["2019"]["mpu"]) == ("42375", "137", "35341")
    assert (linhas["2026"]["vd_novos"], linhas["2026"]["mpu"]) == ("82111", "73138")


def test_agg_volume_conta_por_serie(base):
    tot = lambda s: um(base, "SELECT sum(n) FROM gold.agg_volume WHERE ano_ajuizamento=%s AND serie=%s",
                       ANO, s)[0]
    assert tot("ampliada") == 8 and tot("estrita") == 7  # V1 (só 5560) só na ampliada
    assert um(base, "SELECT sum(n) FROM gold.agg_volume_jan_ago WHERE ano_ajuizamento=%s AND serie='ampliada'",
              ANO)[0] == 8
    assert um(base, "SELECT bool_or(ano_parcial) FROM gold.agg_volume WHERE ano_ajuizamento=%s", ANO)[0] is False


def test_agg_categoria_estrita_ignora_somente_ampliada(base):
    def n(serie):
        return um(base, "SELECT sum(n) FROM gold.agg_categoria WHERE ano_ajuizamento=%s AND tipo_procedimento='ACAO_PENAL'"
                  " AND categoria='FISICA' AND serie=%s", ANO, serie)[0]
    assert n("ampliada") == 2 and n("estrita") == 1


def test_agg_mpu_resultados(base):
    r = um(base, "SELECT sum(n), sum(n_com_decisao), sum(n_deferimento), sum(n_parcial),"
                 " sum(n_indeferimento), sum(n_revogadas) FROM gold.agg_mpu"
                 " WHERE ano_ajuizamento=%s AND serie='ampliada'", ANO)
    assert tuple(r) == (4, 4, 2, 1, 1, 1)


def test_agg_mpu_medida_le_complementos(base):
    assert um(base, "SELECT sum(n) FROM gold.agg_mpu_medida WHERE ano_ajuizamento=%s AND tipo_medida=%s",
              ANO, MED)[0] == 2


def test_agg_cautelar_codigos(base):
    r = um(base, "SELECT sum(n), sum(n_flagrante), sum(n_preventiva),"
                 " sum(n_liberdade_provisoria_concedida) FROM gold.agg_cautelar"
                 " WHERE ano_ajuizamento=%s AND categoria='FEMINICIDIO' AND serie='ampliada'", ANO)
    assert tuple(r) == (1, 1, 1, 1)


def test_agg_cobertura_usa_ref_cnj(base):
    rows = dict((m, (nb, nc, float(p))) for m, nb, nc, p in base.execute(
        "SELECT medida, n_base, n_cnj, pct FROM gold.agg_cobertura_cnj WHERE ano_ajuizamento=%s", (ANO,)))
    assert rows["vd_sem_cartas"] == (7, 1000, 0.7)
    assert rows["mpu"] == (4, 100, 4.0)
    assert rows["feminicidio_acao_penal"] == (1, 10, 10.0)


def test_agg_qualidade_orgao_sem_supressao(base):
    r = um(base, "SELECT n, media_movimentos, mediana_movimentos FROM gold.agg_qualidade_orgao"
                 " WHERE orgao_codigo=9731")
    assert r[0] == 8 and r[0] < 10
    assert float(r[1]) == 1.0 and float(r[2]) == 1.0  # movimentos: 0,0,3,0,1,1,1,2


def test_agg_pipeline_resumo_execucao_gold(base):
    base.execute("INSERT INTO controle.execucao_gold (versao_regras, construida_em)"
                 " VALUES ('teste-2099', '2099-01-01')")
    executar_transformacoes(base)
    assert um(base, "SELECT n > 0 FROM gold.agg_pipeline WHERE versao_regras='teste-2099'")[0]


def test_agg_pipeline_tem_execucao(base):
    assert um(base, "SELECT n FROM gold.agg_pipeline WHERE run_id='T5'")[0] == 8


def _tabelas(conn):
    return [r[0] for r in conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='gold'"
        " AND table_name LIKE 'agg_%'")]


def test_agg_sem_identificadores(base):
    tabs = _tabelas(base)
    assert tabs
    cols = {r[0] for r in base.execute(
        "SELECT column_name FROM information_schema.columns WHERE table_schema='gold'"
        " AND table_name LIKE 'agg_%'")}
    assert not cols & {"registro_id", "numero_processo", "api_id"}


def test_todo_agg_tem_pergunta_e_n(base):
    for t in _tabelas(base):
        cols = {r[0] for r in base.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_schema='gold'"
            " AND table_name=%s", (t,))}
        assert {"pergunta", "n"} <= cols, t
