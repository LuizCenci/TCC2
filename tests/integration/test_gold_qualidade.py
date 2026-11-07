from datetime import datetime

import pytest

from datajud_tcc.gold import qualidade
from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.referencias import carregar_referencias
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]

AJ = datetime(2026, 3, 10, 9, 0, 0)


@pytest.fixture(scope="module")
def base(conn_banco_modulo):
    conn = conn_banco_modulo
    aplicar_esquema(conn)
    aplicar_esquema_gold(conn)
    carregar_territorio(conn)
    carregar_referencias(conn)
    inserir_execucao(conn, "T5", utc(2030, 7, 1), [2026])
    dup = [(11423, utc(2026, 3, 12)), (11423, utc(2026, 3, 12))]
    ids = {
        "OK": inserir_registro(conn, "T5", "api-ok", ano=2026, classe=1268, orgao=1,
                               municipio=4106902, ajuizamento=AJ, assuntos=(10949,),
                               movimentos=[(11423, utc(2026, 3, 12))], numero="T5-OK"),
        "SEM": inserir_registro(conn, "T5", "api-sem", ano=2026, classe=1268, orgao=1,
                                municipio=9999999, ajuizamento=AJ, assuntos=(10949,),
                                numero="T5-SEM"),
        "DUP": inserir_registro(conn, "T5", "api-dup", ano=2026, classe=1268, orgao=1,
                                municipio=4106902, ajuizamento=AJ, assuntos=(10949,),
                                movimentos=dup, numero="T5-DUP"),
    }
    executar_transformacoes(conn)
    ids["conn"] = conn
    return ids


def test_sem_mapeamento_aparece_na_qualidade(base):
    c = base["conn"]
    r = c.execute("SELECT sem_mesorregiao FROM gold.qualidade_sem_mapeamento"
                  " WHERE registro_id=%s", (base["SEM"],)).fetchall()
    assert r == [(True,)]
    assert c.execute("SELECT count(*) FROM gold.fato_processo WHERE registro_id=%s",
                     (base["SEM"],)).fetchone()[0] == 1
    assert c.execute("SELECT count(*) FROM gold.qualidade_sem_mapeamento"
                     " WHERE registro_id=%s", (base["OK"],)).fetchone()[0] == 0


def test_resumo_chaves_e_valores(base):
    c = base["conn"]
    r = qualidade.resumo(c)
    assert set(r) == {"registros", "sem_mesorregiao", "tipo_outros_pct", "sem_categoria_pct",
                      "eventos_antes_ajuizamento", "numero_repetido", "removido_indice",
                      "movimentos_duplicados_processos"}
    assert r["registros"] >= 3 and r["sem_mesorregiao"] >= 1
    assert r["movimentos_duplicados_processos"] >= 1
    assert 0 <= r["tipo_outros_pct"] <= 100 and 0 <= r["sem_categoria_pct"] <= 100
    n = c.execute("SELECT count(*) FROM gold.qualidade_sem_mapeamento WHERE sem_mesorregiao"
                  ).fetchone()[0]
    assert r["sem_mesorregiao"] == n


def test_movimentos_duplicados(base):
    c = base["conn"]
    assert c.execute("SELECT count(*) FROM silver.movimento WHERE registro_id=%s",
                     (base["DUP"],)).fetchone()[0] == 2
    n = c.execute("SELECT n_processos FROM gold.qualidade_movimentos_duplicados"
                  " WHERE orgao_codigo=1").fetchone()[0]
    assert n >= 1
    # OK não tem duplicata: contagem do órgão cobre apenas processos com duplicatas
    tot = c.execute(
        """SELECT count(DISTINCT registro_id) FROM (
               SELECT registro_id FROM silver.movimento m
                 JOIN gold.fato_processo USING (registro_id)
                GROUP BY registro_id, codigo, data_hora HAVING count(*) > 1) x""").fetchone()[0]
    assert tot == sum(x[0] for x in c.execute(
        "SELECT n_processos FROM gold.qualidade_movimentos_duplicados").fetchall())
