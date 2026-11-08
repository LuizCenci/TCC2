import pandas as pd

from painel.dados import carregar_tabela
from painel.rotulos import (CATEGORIA, DESFECHO, MARCO, MEDIDA_COBERTURA,
                            TIPO_PROCEDIMENTO, rotulo_medida)


def test_rotulo_medida_mojibake():
    assert rotulo_medida("Encaminhamento À  família") == "Encaminhamento à família"
    assert rotulo_medida("Restituição de bens indevidamente subtraídos pelo agressor Ã  ofendida (art. 24") == \
        "Restituição de bens indevidamente subtraídos pelo agressor à ofendida (art. 24…)"


def test_rotulo_medida_capitaliza():
    assert rotulo_medida("inclusão em programa de acolhimento familiar") == "Inclusão em programa de acolhimento familiar"


def test_rotulos_cobrem_dados():
    casos = [("agg_taxa", "tipo_procedimento", TIPO_PROCEDIMENTO),
             ("agg_categoria", "categoria", CATEGORIA),
             ("agg_desfecho", "desfecho", DESFECHO),
             ("agg_tempo", "marco", MARCO),
             ("agg_cobertura_cnj", "medida", MEDIDA_COBERTURA)]
    for tabela, col, mapa in casos:
        valores = set(carregar_tabela(tabela)[col].dropna()) - {""}
        assert valores, tabela
        assert valores <= set(mapa), (tabela, valores - set(mapa))
