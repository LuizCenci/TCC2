import pytest


def _abrir():
    psycopg = pytest.importorskip("psycopg", reason="psycopg não instalado")
    from datajud_tcc.silver.conexao import conectar

    try:
        conn = conectar()
    except RuntimeError:
        pytest.skip("DATABASE_URL não configurado")
    except psycopg.Error:
        pytest.skip("conexão com o banco indisponível")
    return conn


@pytest.fixture
def conn_banco():
    """Conexão em transação, sempre revertida e fechada ao final."""
    conn = _abrir()
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture(scope="module")
def conn_banco_modulo():
    """Como conn_banco, mas uma conexão por módulo (revertida ao final do módulo)."""
    conn = _abrir()
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()
