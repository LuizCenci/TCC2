import pytest

from painel.dados import (
    ErroIntegridade, carregar_manifesto, carregar_tabela,
    total_processos, verificar_integridade,
)


def test_integridade_ok():
    verificar_integridade()


def test_integridade_detecta_alteracao(pasta_copia):
    alvo = pasta_copia / "agg_mpu.csv"
    alvo.write_bytes(alvo.read_bytes() + b"\n")
    with pytest.raises(ErroIntegridade, match="agg_mpu.csv"):
        verificar_integridade(pasta_copia)


def test_integridade_detecta_ausencia(pasta_copia):
    (pasta_copia / "agg_taxa.csv").unlink()
    with pytest.raises(ErroIntegridade, match="agg_taxa.csv"):
        verificar_integridade(pasta_copia)


def test_manifesto():
    m = carregar_manifesto()
    assert m["versao_regras"] == "gold-2026-11-11"
    assert m["data_corte_max"] == "2026-11-05"
    assert len(m["arquivos"]) == 12


def test_carregar_tabela_tipos():
    t = carregar_tabela("agg_taxa")
    assert t["suprimido"].dtype == bool
    assert str(t["n"].dtype) == "Int64"
    assert t.loc[t["suprimido"], "n"].isna().all()


def test_total_processos():
    assert total_processos() == 147020


def test_chaves_inteiras():
    for nome in ("agg_taxa", "agg_volume", "agg_volume_jan_ago"):
        t = carregar_tabela(nome)
        for col in ("ano_ajuizamento", "mes_ajuizamento", "mesorregiao_id"):
            if col in t.columns:
                assert str(t[col].dtype) == "Int64", (nome, col)
    assert (carregar_tabela("agg_taxa").ano_ajuizamento == 2025).sum() > 0
    assert str(carregar_tabela("agg_qualidade_orgao")["orgao_codigo"].dtype) == "Int64"


def test_integridade_conteudo_commitado():
    import hashlib
    import subprocess
    from painel import config
    rel = config.PASTA_EXPORTACAO.relative_to(config.RAIZ_REPO).as_posix()
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, cwd=config.RAIZ_REPO)
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git indisponível")
    for item in carregar_manifesto()["arquivos"]:
        blob = subprocess.run(["git", "show", f"HEAD:{rel}/{item['arquivo']}"], check=True,
                              capture_output=True, cwd=config.RAIZ_REPO).stdout
        assert hashlib.sha256(blob).hexdigest() == item["sha256"], item["arquivo"]
