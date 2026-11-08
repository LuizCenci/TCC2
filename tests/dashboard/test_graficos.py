import pandas as pd

from painel.graficos import (COR_PRINCIPAL, figura_barras, figura_incidencia,
                             figura_linhas)


def test_figura_linhas_suprimido_vira_lacuna():
    df = pd.DataFrame({"mes": [1, 2, 3], "n": pd.array([10, None, 12], dtype="Int64"),
                       "suprimido": [False, True, False]})
    fig = figura_linhas(df, "mes", "n", None, "t", "processos públicos")
    ys = list(fig.data[0].y)
    assert ys[1] is None and 0 not in ys


def test_figura_barras_tudo_suprimido():
    df = pd.DataFrame({"x": ["a", "b"], "n": pd.array([None, None], dtype="Int64"),
                       "suprimido": [True, True]})
    assert figura_barras(df, "x", "n", None, "t", "processos públicos") is None


def test_figura_usa_paleta_lilas():
    df = pd.DataFrame({"x": ["a", "b"], "n": pd.array([5, 7], dtype="Int64"),
                       "suprimido": [False, False]})
    fig = figura_barras(df, "x", "n", None, "t", "processos públicos")
    assert fig.data[0].marker.color == COR_PRINCIPAL


def test_figura_barras_omite_suprimidas():
    df = pd.DataFrame({"x": ["a", "b"], "n": pd.array([5, None], dtype="Int64"),
                       "suprimido": [False, True]})
    fig = figura_barras(df, "x", "n", None, "t", "processos públicos")
    assert list(fig.data[0].x) == ["a"]


def test_figura_incidencia_anos():
    df = pd.DataFrame({"desfecho": ["d", "e"], "ia_365": [0.1, 0.2], "ia_730": [0.2, 0.3],
                       "ia_1095": [0.3, 0.4], "ia_1825": [0.4, 0.5]})
    fig = figura_incidencia(df)
    assert len(fig.data) == 2 and list(fig.data[0].x) == [1, 2, 3, 5]
