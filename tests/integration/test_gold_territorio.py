import pytest

from datajud_tcc.gold.territorio import carregar_territorio

pytestmark = pytest.mark.banco


def test_carrega_399_municipios_10_mesorregioes(conn_banco):
    assert carregar_territorio(conn_banco) == {"municipios": 399, "mesorregioes": 10}


def test_geometrias_validas_srid_4674(conn_banco):
    carregar_territorio(conn_banco)
    for t in ("ref.municipio", "ref.mesorregiao"):
        r = conn_banco.execute(
            f"SELECT bool_and(ST_IsValid(geom)), min(ST_SRID(geom)), max(ST_SRID(geom)) FROM {t}"
        ).fetchone()
        assert r == (True, 4674, 4674)


def test_todo_municipio_em_uma_mesorregiao(conn_banco):
    carregar_territorio(conn_banco)
    r = conn_banco.execute(
        """SELECT count(*) FROM ref.municipio m
           LEFT JOIN ref.mesorregiao r USING (mesorregiao_id)
           WHERE r.mesorregiao_id IS NULL"""
    ).fetchone()[0]
    assert r == 0
    assert conn_banco.execute("SELECT sum(n_municipios) FROM ref.mesorregiao").fetchone()[0] == 399


def test_area_mesorregioes_igual_estado(conn_banco):
    carregar_territorio(conn_banco)
    soma, uniao = conn_banco.execute(
        """SELECT (SELECT sum(ST_Area(geom::geography)) FROM ref.mesorregiao),
                  (SELECT ST_Area(ST_Union(geom)::geography) FROM ref.mesorregiao)"""
    ).fetchone()
    assert 0.999 <= soma / uniao <= 1.001


def test_populacao_por_mesorregiao(conn_banco):
    carregar_territorio(conn_banco)
    pop = conn_banco.execute(
        "SELECT pop_feminina_censo2022 FROM ref.mesorregiao WHERE mesorregiao = 'Metropolitana de Curitiba'"
    ).fetchone()[0]
    assert pop == 1997133


def test_carga_territorio_idempotente(conn_banco):
    a = carregar_territorio(conn_banco)
    b = carregar_territorio(conn_banco)
    assert a == b
    assert conn_banco.execute("SELECT count(*) FROM ref.municipio").fetchone()[0] == 399
