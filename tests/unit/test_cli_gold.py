from datajud_tcc import cli
from datajud_tcc.gold import construcao, referencias
from datajud_tcc.silver import conexao

DSN_SECRETO = "postgresql://u:senha@h/db"


class _Conn:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass

    def close(self):
        pass


def test_cli_gold_construir_sem_dsn(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(referencias, "ler_regras", lambda *a: {"versao_regras": "v"})
    monkeypatch.setenv("DATABASE_URL", DSN_SECRETO)
    conn = _Conn()
    monkeypatch.setattr(conexao, "conectar", lambda dsn=None: conn)
    monkeypatch.setattr(construcao, "construir_gold", lambda c, v: {"processos": 3, "eventos": 5})
    assert cli.main(["gold-construir"]) == 0
    saida = capsys.readouterr()
    assert "processos=3" in saida.out
    assert "postgresql://" not in saida.out + saida.err
    assert conn.commits == 1


def test_cli_gold_construir_versao_invalida_retorna_3(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(referencias, "ler_regras", lambda *a: {"versao_regras": "v"})
    monkeypatch.setenv("DATABASE_URL", DSN_SECRETO)
    monkeypatch.setattr(conexao, "conectar", lambda dsn=None: _Conn())

    def falha(c, v):
        raise ValueError("versão divergente")

    monkeypatch.setattr(construcao, "construir_gold", falha)
    assert cli.main(["gold-construir"]) == 3
    assert "postgresql://" not in capsys.readouterr().err
