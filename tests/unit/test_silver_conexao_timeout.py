"""conectar() deve limitar o tempo de conexão."""
import psycopg

from datajud_tcc.silver.conexao import conectar


def test_conectar_passa_connect_timeout(monkeypatch):
    capturado = {}

    def falso(dsn, **kwargs):
        capturado.update(kwargs)
        return object()

    monkeypatch.setattr(psycopg, "connect", falso)
    conectar("postgresql://x")
    assert capturado["connect_timeout"] == 10
