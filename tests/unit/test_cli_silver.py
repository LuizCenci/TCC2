"""Testes dos subcomandos Silver da CLI (sem banco real)."""
from pathlib import Path

from datajud_tcc import cli
from datajud_tcc.silver import carga, conexao, esquema

DSN_SECRETO = "postgresql://usuario:segredo@host/db"


class _ConnFalsa:
    def __init__(self):
        self.commits = 0
        self.fechada = False

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass

    def close(self):
        self.fechada = True


def _prepara(monkeypatch, carregar):
    conn = _ConnFalsa()
    monkeypatch.setattr(conexao, "conectar", lambda dsn=None: conn)
    monkeypatch.setattr(esquema, "aplicar_esquema", lambda c: None)
    monkeypatch.setattr(carga, "carregar_execucao", carregar)
    return conn


def test_cli_silver_carregar_imprime_contagens_sem_dsn(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("DATABASE_URL", DSN_SECRETO)
    conn = _prepara(monkeypatch, lambda c, r: {
        "paginas": 1, "registros": 3, "assuntos": 3, "movimentos": 5, "complementos": 2})
    codigo = cli.main(["silver-carregar", "--run-root", str(tmp_path)])
    saida = capsys.readouterr()
    assert codigo == 0
    assert "registros=3" in saida.out
    assert "postgresql://" not in saida.out + saida.err
    assert conn.commits == 1 and conn.fechada


def test_cli_silver_carregar_execucao_invalida_retorna_3(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("DATABASE_URL", DSN_SECRETO)

    def falha(c, r):
        raise carga.ExecucaoInvalida("manifesto ausente")

    conn = _prepara(monkeypatch, falha)
    codigo = cli.main(["silver-carregar", "--run-root", str(tmp_path)])
    saida = capsys.readouterr()
    assert codigo == 3
    assert "manifesto ausente" in saida.err
    assert "postgresql://" not in saida.out + saida.err
    assert conn.commits == 0 and conn.fechada
