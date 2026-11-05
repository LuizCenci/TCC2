import pytest

from datajud_tcc import cli
from datajud_tcc.silver.conexao import obter_dsn


def test_obter_dsn_le_variavel_de_ambiente(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://a:b@h/x")
    assert obter_dsn() == "postgresql://a:b@h/x"


def test_obter_dsn_le_do_env(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text(
        "DATAJUD_API_KEY=x\nDATABASE_URL=postgresql://u:p@h/db\n", encoding="utf-8"
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.chdir(tmp_path)
    assert obter_dsn() == "postgresql://u:p@h/db"


def test_obter_dsn_ausente_levanta_sem_expor(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError) as exc:
        obter_dsn()
    assert "postgresql://" not in str(exc.value)


def test_load_dotenv_padrao_continua_lendo_chave_api(monkeypatch, tmp_path):
    env = tmp_path / ".env"
    env.write_text("DATAJUD_API_KEY=abc\nDATABASE_URL=postgresql://u:p@h/db\n", encoding="utf-8")
    monkeypatch.delenv("DATAJUD_API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    cli._load_dotenv(env)
    import os

    assert os.environ["DATAJUD_API_KEY"] == "abc"
    assert "DATABASE_URL" not in os.environ
    monkeypatch.delenv("DATAJUD_API_KEY", raising=False)
