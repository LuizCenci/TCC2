from datetime import datetime, timezone

import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.referencias import carregar_referencias
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]

AJ = datetime(2026, 3, 10, 9, 0, 0)

CENARIOS = {
    "E1": [(581, utc(2026, 3, 11)), (11423, utc(2026, 3, 12))],
    "M1": [(26, utc(2026, 3, 11)), (11423, utc(2026, 3, 12)), (11424, utc(2026, 3, 20)),
           (11426, utc(2026, 4, 1)), (26, utc(2026, 5, 1))],
    "D1": [(221, utc(2026, 4, 1))],
    "D2": [(221, utc(2026, 5, 1)), (471, utc(2026, 4, 1))],
    "A1": [(246, utc(2026, 4, 5))],
    "A2": [(246, utc(2026, 4, 5)), (849, utc(2026, 5, 5))],
    "A3": [(246, utc(2026, 4, 5, 8)), (849, utc(2026, 4, 5, 15))],
    "C1": [(11423, utc(2026, 3, 12))],
    "B1": [(221, utc(2026, 3, 1)), (11423, utc(2026, 3, 12))],
    "N1": [(11423, None)],
    "MN1": [(11423, datetime(2026, 3, 10, 23, 30, tzinfo=timezone.utc))],
    "MN2": [(11423, datetime(2026, 3, 10, 8, 0, tzinfo=timezone.utc))],
    "K1": [(221, utc(2026, 4, 1))],
    "K2": [],
}


@pytest.fixture(scope="module")
def base(conn_banco_modulo):
    conn = conn_banco_modulo
    aplicar_esquema(conn)
    aplicar_esquema_gold(conn)
    carregar_territorio(conn)
    carregar_referencias(conn)
    inserir_execucao(conn, "T4", utc(2030, 6, 1), [2026])
    ids = {n: inserir_registro(conn, "T4", f"api-{n}", ano=2026, classe=1268, orgao=1,
                               municipio=4106902, ajuizamento=AJ, assuntos=(10949,),
                               movimentos=m, numero=n)
           for n, m in CENARIOS.items()}
    executar_transformacoes(conn)
    ids["conn"] = conn
    return ids


def fato(base, n):
    cur = base["conn"].execute("SELECT * FROM gold.fato_processo WHERE registro_id=%s",
                               (base[n],))
    cols = [d.name for d in cur.description]
    return dict(zip(cols, cur.fetchone()))


def test_evento_so_com_fase(base):
    rows = base["conn"].execute(
        "SELECT movimento_codigo, fase, subtipo FROM gold.fato_evento WHERE registro_id=%s",
        (base["E1"],)).fetchall()
    assert rows == [(11423, "DECISAO_MPU", "DEFERIMENTO")]


def test_marcos_primeira_ocorrencia(base):
    f = fato(base, "M1")
    assert str(f["dt_distribuicao"]) == "2026-03-11"
    assert str(f["dt_decisao_mpu"]) == "2026-03-12" and f["resultado_mpu"] == "DEFERIMENTO"
    assert str(f["dt_revogacao_mpu"]) == "2026-04-01"


def test_desfecho_condenacao_parcial(base):
    f = fato(base, "D1")
    assert (f["desfecho"], f["desfecho_subtipo"]) == ("CONDENACAO", "PARCIAL")
    assert str(f["dt_desfecho"]) == "2026-04-01" and f["censurado"] is False
    assert f["duracao_dias"] == 22 and str(f["dt_sentenca"]) == "2026-04-01"


def test_desfecho_primeiro_evento_vence(base):
    assert fato(base, "D2")["desfecho"] == "PRESCRICAO"


def test_encerrado_sem_desfecho(base):
    f = fato(base, "A1")
    assert f["desfecho"] == "ENCERRADO_SEM_DESFECHO" and str(f["dt_desfecho"]) == "2026-04-05"
    assert str(f["dt_arquivamento"]) == "2026-04-05" and f["reativado"] is False


def test_reativado(base):
    assert fato(base, "A2")["reativado"] is True


def test_reativacao_no_mesmo_dia_do_arquivamento_nao_conta_como_reativado(base):
    # regra atual: comparação estrita (data da reativação > data do arquivamento)
    assert fato(base, "A3")["reativado"] is False


def test_em_andamento_censurado(base):
    f = fato(base, "C1")
    assert f["desfecho"] == "EM_ANDAMENTO" and f["censurado"] is True
    assert f["dt_desfecho"] is None
    assert f["duracao_dias"] == (datetime(2030, 6, 1).date() - AJ.date()).days


def test_evento_antes_do_ajuizamento_e_ignorado(base):
    f = fato(base, "B1")
    assert f["evento_antes_ajuizamento"] is True and f["desfecho"] == "EM_ANDAMENTO"
    assert f["dt_sentenca"] is None and str(f["dt_decisao_mpu"]) == "2026-03-12"


def test_movimento_mapeado_com_data_nula_e_sinalizado_e_excluido_dos_marcos(base):
    f = fato(base, "N1")
    assert f["evento_antes_ajuizamento"] is True
    assert f["dt_decisao_mpu"] is None and f["desfecho"] == "EM_ANDAMENTO"
    n = base["conn"].execute("SELECT count(*) FROM gold.fato_evento WHERE registro_id=%s",
                             (base["N1"],)).fetchone()[0]
    assert n == 1


def test_perto_da_meia_noite_no_dia_do_ajuizamento_mantido(base):
    f = fato(base, "MN1")
    assert f["evento_antes_ajuizamento"] is False
    assert str(f["dt_decisao_mpu"]) == "2026-03-10"


def test_evento_horas_antes_do_ajuizamento_no_mesmo_dia_e_sinalizado(base):
    f = fato(base, "MN2")
    d = base["conn"].execute(
        "SELECT dias_desde_ajuizamento FROM gold.fato_evento WHERE registro_id=%s",
        (base["MN2"],)).fetchone()[0]
    assert d == -1
    assert f["evento_antes_ajuizamento"] is True and f["dt_decisao_mpu"] is None


def test_censurado_consistente(base):
    ruins = base["conn"].execute(
        """SELECT count(*) FROM gold.fato_processo WHERE censurado IS DISTINCT FROM
               (desfecho = 'EM_ANDAMENTO')
            OR (dt_desfecho IS NOT NULL AND dt_desfecho < data_ajuizamento::date)""").fetchone()[0]
    assert ruins == 0
