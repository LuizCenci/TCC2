import pytest


@pytest.fixture
def conn_banco():
    """Conexão em transação, sempre revertida e fechada ao final."""
    psycopg = pytest.importorskip("psycopg", reason="psycopg não instalado")
    from datajud_tcc.silver.conexao import conectar

    try:
        conn = conectar()
    except RuntimeError:
        pytest.skip("DATABASE_URL não configurado")
    except psycopg.Error:
        pytest.skip("conexão com o banco indisponível")
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()
