from pathlib import Path

from datajud_tcc import cli
from datajud_tcc.gold import referencias
from datajud_tcc.gold.metodos import construcao, exportacao
from datajud_tcc.silver import conexao

DSN_SECRETO = "postgresql://u:senha@h/db"


class _Conn:
    commits = 0

    def commit(self):
        self.commits += 1

    def rollback(self):
        pass

    def close(self):
        pass


def test_cli_gold_agregados_sem_dsn(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(referencias, "ler_regras", lambda *a: {"versao_regras": "v"})
    monkeypatch.setenv("DATABASE_URL", DSN_SECRETO)
    conn = _Conn()
    monkeypatch.setattr(conexao, "conectar", lambda dsn=None: conn)
    monkeypatch.setattr(construcao, "construir_agregados", lambda c, v: {"agg_taxa": 4})
    assert cli.main(["gold-agregados"]) == 0
    saida = capsys.readouterr()
    assert "agg_taxa=4" in saida.out
    assert "postgresql://" not in saida.out + saida.err
    assert conn.commits == 1


def test_cli_gold_agregados_versao_invalida_retorna_3(monkeypatch, capsys, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(referencias, "ler_regras", lambda *a: {"versao_regras": "v"})
    monkeypatch.setenv("DATABASE_URL", DSN_SECRETO)
    monkeypatch.setattr(conexao, "conectar", lambda dsn=None: _Conn())

    def falha(c, v):
        raise ValueError("divergente")

    monkeypatch.setattr(construcao, "construir_agregados", falha)
    assert cli.main(["gold-agregados"]) == 3
    assert "postgresql://" not in capsys.readouterr().err


def test_cli_gold_exportar_imprime_pasta(monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", DSN_SECRETO)
    monkeypatch.setattr(conexao, "conectar", lambda dsn=None: _Conn())
    monkeypatch.setattr(exportacao, "exportar", lambda c, destino: Path("x") / "pub-1")
    assert cli.main(["gold-exportar", "--destino", "x"]) == 0
    saida = capsys.readouterr()
    assert "pub-1" in saida.out
    assert "postgresql://" not in saida.out + saida.err
