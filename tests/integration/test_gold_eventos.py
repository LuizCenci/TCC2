from datetime import datetime

import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.referencias import carregar_referencias
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = pytest.mark.banco

AJ = datetime(2026, 3, 10, 9, 0, 0)


@pytest.fixture
def base(conn_banco):
    aplicar_esquema(conn_banco)
    aplicar_esquema_gold(conn_banco)
    carregar_territorio(conn_banco)
    carregar_referencias(conn_banco)
    inserir_execucao(conn_banco, "T4", utc(2030, 6, 1), [2026])
    return conn_banco


def reg(conn, n, movs):
    return inserir_registro(conn, "T4", f"api-{n}", ano=2026, classe=1268, orgao=1,
                            municipio=4106902, ajuizamento=AJ, assuntos=(10949,),
                            movimentos=movs, numero=n)


def fato(conn, rid):
    cur = conn.execute("SELECT * FROM gold.fato_processo WHERE registro_id=%s", (rid,))
    cols = [d.name for d in cur.description]
    return dict(zip(cols, cur.fetchone()))


def test_evento_so_com_fase(base):
    rid = reg(base, "E1", [(581, utc(2026, 3, 11)), (11423, utc(2026, 3, 12))])
    executar_transformacoes(base)
    rows = base.execute("SELECT movimento_codigo, fase, subtipo FROM gold.fato_evento"
                        " WHERE registro_id=%s", (rid,)).fetchall()
    assert rows == [(11423, "DECISAO_MPU", "DEFERIMENTO")]


def test_marcos_primeira_ocorrencia(base):
    rid = reg(base, "M1", [(26, utc(2026, 3, 11)), (11423, utc(2026, 3, 12)),
                           (11424, utc(2026, 3, 20)), (11426, utc(2026, 4, 1)),
                           (26, utc(2026, 5, 1))])
    executar_transformacoes(base)
    f = fato(base, rid)
    assert str(f["dt_distribuicao"]) == "2026-03-11"
    assert str(f["dt_decisao_mpu"]) == "2026-03-12" and f["resultado_mpu"] == "DEFERIMENTO"
    assert str(f["dt_revogacao_mpu"]) == "2026-04-01"


def test_desfecho_condenacao_parcial(base):
    rid = reg(base, "D1", [(221, utc(2026, 4, 1))])
    executar_transformacoes(base)
    f = fato(base, rid)
    assert (f["desfecho"], f["desfecho_subtipo"]) == ("CONDENACAO", "PARCIAL")
    assert str(f["dt_desfecho"]) == "2026-04-01" and f["censurado"] is False
    assert f["duracao_dias"] == 22 and str(f["dt_sentenca"]) == "2026-04-01"


def test_desfecho_primeiro_evento_vence(base):
    rid = reg(base, "D2", [(221, utc(2026, 5, 1)), (471, utc(2026, 4, 1))])
    executar_transformacoes(base)
    assert fato(base, rid)["desfecho"] == "PRESCRICAO"


def test_encerrado_sem_desfecho(base):
    rid = reg(base, "A1", [(246, utc(2026, 4, 5))])
    executar_transformacoes(base)
    f = fato(base, rid)
    assert f["desfecho"] == "ENCERRADO_SEM_DESFECHO" and str(f["dt_desfecho"]) == "2026-04-05"
    assert str(f["dt_arquivamento"]) == "2026-04-05" and f["reativado"] is False


def test_reativado(base):
    rid = reg(base, "A2", [(246, utc(2026, 4, 5)), (849, utc(2026, 5, 5))])
    executar_transformacoes(base)
    assert fato(base, rid)["reativado"] is True


def test_em_andamento_censurado(base):
    rid = reg(base, "C1", [(11423, utc(2026, 3, 12))])
    executar_transformacoes(base)
    f = fato(base, rid)
    assert f["desfecho"] == "EM_ANDAMENTO" and f["censurado"] is True
    assert f["dt_desfecho"] is None
    assert f["duracao_dias"] == (datetime(2030, 6, 1).date() - AJ.date()).days


def test_evento_antes_do_ajuizamento_e_ignorado(base):
    rid = reg(base, "B1", [(221, utc(2026, 3, 1)), (11423, utc(2026, 3, 12))])
    executar_transformacoes(base)
    f = fato(base, rid)
    assert f["evento_antes_ajuizamento"] is True and f["desfecho"] == "EM_ANDAMENTO"
    assert f["dt_sentenca"] is None and str(f["dt_decisao_mpu"]) == "2026-03-12"


def test_censurado_consistente(base):
    reg(base, "K1", [(221, utc(2026, 4, 1))])
    reg(base, "K2", [])
    executar_transformacoes(base)
    ruins = base.execute(
        """SELECT count(*) FROM gold.fato_processo WHERE censurado IS DISTINCT FROM
               (desfecho = 'EM_ANDAMENTO')
            OR (dt_desfecho IS NOT NULL AND dt_desfecho < data_ajuizamento::date)""").fetchone()[0]
    assert ruins == 0
