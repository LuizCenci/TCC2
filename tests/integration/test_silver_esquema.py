import pytest

from datajud_tcc.silver.esquema import aplicar_esquema

pytestmark = pytest.mark.banco

TABELAS = {
    ("controle", "execucao_coleta"),
    ("controle", "pagina_bronze"),
    ("silver", "registro"),
    ("silver", "registro_assunto"),
    ("silver", "movimento"),
    ("silver", "complemento_movimento"),
    ("restrito", "identificador"),
}


def test_aplicar_esquema_cria_tabelas_e_e_idempotente(conn_banco):
    aplicar_esquema(conn_banco)
    aplicar_esquema(conn_banco)
    esquemas = ("controle", "silver", "restrito")
    tabelas = set(
        conn_banco.execute(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_schema = ANY(%s)",
            (list(esquemas),),
        ).fetchall()
    )
    assert TABELAS <= tabelas
    colunas = conn_banco.execute(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_schema = ANY(%s) AND column_name = 'em_analise'",
        (list(esquemas),),
    ).fetchall()
    assert colunas == []
