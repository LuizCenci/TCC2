from datetime import datetime

import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.referencias import carregar_referencias
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]

AJ = datetime(2026, 3, 10, 9, 0, 0)


def reg(conn, run, api, n, *, assuntos=(10949,), classe=1268, orgao=1, mun=4106902, ano=2026):
    return inserir_registro(conn, run, api, ano=ano, classe=classe, orgao=orgao,
                            municipio=mun, ajuizamento=AJ, assuntos=assuntos, numero=n)


@pytest.fixture(scope="module")
def base(conn_banco_modulo):
    """Todos os cenários inseridos de uma vez; transformações rodam uma única vez.

    Execuções completas usadas nos cenários de remoção ficam em datas distintas
    (2031, 2033) para que não interfiram nos demais cenários.
    """
    conn = conn_banco_modulo
    aplicar_esquema(conn)
    aplicar_esquema_gold(conn)
    carregar_territorio(conn)
    carregar_referencias(conn)
    d = {}
    # versão mais recente
    inserir_execucao(conn, "T3-a", utc(2030, 1, 1), [2026])
    inserir_execucao(conn, "T3-b", utc(2030, 2, 1), [2026])
    inserir_execucao(conn, "T3-c", utc(2030, 3, 1), [], updated_since="2030-02-01")
    d["v1"] = reg(conn, "T3-a", "api-v", "N-v")
    d["v2"] = reg(conn, "T3-b", "api-v", "N-v")
    d["v3"] = reg(conn, "T3-c", "api-v", "N-v")
    # removido do índice
    inserir_execucao(conn, "T3-r1", utc(2031, 10, 18), [2026])
    inserir_execucao(conn, "T3-r2", utc(2031, 11, 5), [2026])
    d["sumiu"] = reg(conn, "T3-r1", "api-sumiu", "N-1")
    reg(conn, "T3-r1", "api-fica", "N-2")
    reg(conn, "T3-r2", "api-fica", "N-2")
    # execução incremental posterior não conta como remoção
    # (T3-i1 é completa e posterior a r2, então "api-fica" também consta nela)
    inserir_execucao(conn, "T3-i1", utc(2033, 10, 18), [2026])
    d["fica"] = reg(conn, "T3-i1", "api-fica", "N-2")
    inserir_execucao(conn, "T3-i2", utc(2033, 11, 5), [], updated_since="2033-10-18")
    d["inc"] = reg(conn, "T3-i1", "api-i", "N-i")
    # demais cenários
    inserir_execucao(conn, "T3-s", utc(2030, 1, 1), [2026])
    d["sa"] = reg(conn, "T3-s", "sa", "N-sa", assuntos=(5560,), classe=999999)
    d["sb"] = reg(conn, "T3-s", "sb", "N-sb", assuntos=(12194, 5560), classe=999999)
    d["sc"] = reg(conn, "T3-s", "sc", "N-sc", assuntos=(10949,), classe=999999)
    d["sd"] = reg(conn, "T3-s", "sd", "N-sd", assuntos=(3402, 10949), classe=999999)
    d["ta"] = reg(conn, "T3-s", "ta", "N-ta", classe=1268, orgao=8766, mun=4106902)
    d["tb"] = reg(conn, "T3-s", "tb", "N-tb", classe=355, orgao=1, mun=1234567)
    d["na"] = reg(conn, "T3-s", "na", "N-rep")
    d["nb"] = reg(conn, "T3-s", "nb", "N-rep")
    d["nc"] = reg(conn, "T3-s", "nc", "N-unico")
    d["fa"] = reg(conn, "T3-s", "fa", "N-fa", assuntos=(12091, 5555))
    d["fb"] = reg(conn, "T3-s", "fb", "N-fb", assuntos=(12091,))
    # catálogo diferente: execução completa posterior não conta como remoção
    inserir_execucao(conn, "T3-k1", utc(2035, 1, 1), [2026], catalogo_sha256="a" * 64)
    d["catalogo"] = reg(conn, "T3-k1", "api-cat", "N-cat")
    inserir_execucao(conn, "T3-k2", utc(2035, 2, 1), [2026], catalogo_sha256="b" * 64)
    reg(conn, "T3-k2", "api-outra", "N-outra")
    # data_corte em UTC, mesmo com fuso de sessão diferente
    inserir_execucao(conn, "T3-u", utc(2030, 3, 10, 1), [2026])
    d["utc"] = reg(conn, "T3-u", "api-utc", "N-utc")
    conn.execute("SET LOCAL TIME ZONE 'America/Sao_Paulo'")
    executar_transformacoes(conn)
    d["conn"] = conn
    return d


def fato(conn, rid):
    cur = conn.execute("SELECT * FROM gold.fato_processo WHERE registro_id=%s", (rid,))
    cols = [d.name for d in cur.description]
    r = cur.fetchone()
    return dict(zip(cols, r)) if r else None


def cats(conn, rid):
    return dict(conn.execute(
        "SELECT categoria, somente_ampliada FROM gold.processo_categoria WHERE registro_id=%s",
        (rid,)).fetchall())


def test_versao_mais_recente_prevalece(base):
    c = base["conn"]
    assert fato(c, base["v1"]) is None and fato(c, base["v2"]) is None
    f = fato(c, base["v3"])
    assert f["run_id"] == "T3-c" and str(f["data_corte"]) == "2030-03-01"


def test_removido_indice(base):
    c = base["conn"]
    assert fato(c, base["sumiu"])["removido_indice"] is True
    assert fato(c, base["fica"])["removido_indice"] is False


def test_removido_indice_incremental_nao_conta(base):
    assert fato(base["conn"], base["inc"])["removido_indice"] is False


def test_series_e_categoria_generica(base):
    c = base["conn"]
    assert fato(c, base["sa"])["serie_estrita"] is False
    assert cats(c, base["sa"]) == {"FISICA": True}
    assert fato(c, base["sb"])["serie_estrita"] is True
    assert cats(c, base["sb"])["FISICA"] is False
    assert cats(c, base["sc"]) == {"VD_SEM_ESPECIFICACAO": False}
    assert set(cats(c, base["sd"])) == {"AMEACA"}


def test_tipo_e_territorio(base):
    c = base["conn"]
    fa, fb = fato(c, base["ta"]), fato(c, base["tb"])
    assert fa["tipo_procedimento"] == "MPU" and fa["mesorregiao_id"] == 4110
    assert fa["orgao_especializado"] is True and fa["serie_estrita"] is True
    assert fb["tipo_procedimento"] == "CARTA" and fb["mesorregiao_id"] is None
    assert fb["orgao_especializado"] is False


def test_numero_repetido(base):
    c = base["conn"]
    assert fato(c, base["na"])["numero_repetido"] and fato(c, base["nb"])["numero_repetido"]
    assert fato(c, base["nc"])["numero_repetido"] is False


def test_feminicidio_tentado(base):
    c = base["conn"]
    assert fato(c, base["fa"])["feminicidio_tentado"] is True
    assert fato(c, base["fb"])["feminicidio_tentado"] is False
    assert "FEMINICIDIO" in cats(c, base["fb"])


def test_gold_sem_identificadores(base):
    cols = {r[0] for r in base["conn"].execute(
        """SELECT column_name FROM information_schema.columns
            WHERE table_schema IN ('gold','ref')""").fetchall()}
    assert not cols & {"numero_processo", "id_source", "api_id"}


def test_removido_indice_exige_mesmo_catalogo(base):
    assert fato(base["conn"], base["catalogo"])["removido_indice"] is False


def test_data_corte_em_utc(base):
    from datetime import date
    assert fato(base["conn"], base["utc"])["data_corte"] == date(2030, 3, 10)
