import csv

from painel.config import ARQUIVO_MESORREGIOES, RAIZ_REPO
from painel.dados import carregar_tabela
from painel.territorio import NOMES_MESORREGIAO, carregar_mesorregioes


def test_dez_mesorregioes():
    g = carregar_mesorregioes()
    assert len(g["features"]) == 10
    assert {f["properties"]["mesorregiao_id"] for f in g["features"]} == set(range(4101, 4111))


def test_nomes_batem_com_referencia():
    with open(RAIZ_REPO / "config" / "gold" / "ref_municipio_pr.csv", encoding="utf-8", newline="") as f:
        esperado = {int(r["mesorregiao_id"]): r["mesorregiao"] for r in csv.DictReader(f)}
    assert NOMES_MESORREGIAO() == esperado


def test_ids_cobrem_agregados():
    assert set(carregar_tabela("agg_taxa")["mesorregiao_id"].dropna().astype(int)) <= set(NOMES_MESORREGIAO())


def test_tamanho_arquivo():
    assert ARQUIVO_MESORREGIOES.stat().st_size < 300_000
