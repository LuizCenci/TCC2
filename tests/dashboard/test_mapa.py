import pandas as pd

from painel.dados import carregar_tabela
from painel.graficos import COR_SUPRIMIDO
from painel.mapa import figura_mapa


def _recorte():
    t = carregar_tabela("agg_taxa")
    return t[(t.ano_ajuizamento == 2025) & (t.tipo_procedimento == "ACAO_PENAL")
             & (t.serie == "estrita")]


def test_mapa_sempre_10_mesorregioes():
    fig = figura_mapa(_recorte().iloc[:3], "taxa_eb_100k", "t")
    locais = set().union(*[set(tr.locations) for tr in fig.data])
    assert locais == set(range(4101, 4111))


def test_mapa_suprimido_cinza():
    r = _recorte().iloc[:3].copy()
    r["suprimido"] = [True, False, False]
    sup = int(r.iloc[0]["mesorregiao_id"])
    fig = figura_mapa(r, "taxa_eb_100k", "t")
    cinzas = [tr for tr in fig.data if all(c[1] == COR_SUPRIMIDO for c in tr.colorscale)]
    assert cinzas and sup in cinzas[0].locations
    assert all(sup not in tr.locations for tr in fig.data if tr not in cinzas)
