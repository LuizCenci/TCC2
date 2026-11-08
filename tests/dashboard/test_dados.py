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
    assert m["versao_regras"] == "gold-2026-11-07"
    assert m["data_corte_max"] == "2026-11-05"
    assert len(m["arquivos"]) == 12


def test_carregar_tabela_tipos():
    t = carregar_tabela("agg_taxa")
    assert t["suprimido"].dtype == bool
    assert str(t["n"].dtype) == "Int64"
    assert t.loc[t["suprimido"], "n"].isna().all()


def test_total_processos():
    assert total_processos() == 147020
