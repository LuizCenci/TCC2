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


def test_figura_incidencia_percentual():
    from painel.dados import carregar_tabela
    t = carregar_tabela("agg_desfecho")
    r = t[(t.tipo_procedimento == "ACAO_PENAL") & (t.serie == "estrita")
          & (t.variante == "principal") & (t.estrato == "coorte")
          & (t.valor_estrato == "2019-2021")]
    fig = figura_incidencia(r)
    tr = next(x for x in fig.data if x.name == "Condenação")
    assert tr.text[-1] == "46,0%"


def _df_series(k):
    linhas = [{"mes": m, "tipo": f"s{i}", "n": 5, "suprimido": False}
              for i in range(k) for m in (1, 2)]
    return pd.DataFrame(linhas)


def test_figura_linhas_simbolos_por_serie():
    fig = figura_linhas(_df_series(3), "mes", "n", "tipo", "t", "r")
    assert [t.marker.symbol for t in fig.data] == ["circle", "x", "triangle-up"]
    assert all(t.marker.size == 8 for t in fig.data)


def test_figura_linhas_simbolos_ciclam():
    fig = figura_linhas(_df_series(9), "mes", "n", "tipo", "t", "r")
    assert fig.data[8].marker.symbol == fig.data[0].marker.symbol == "circle"


def test_figura_linhas_serie_unica_circulo():
    fig = figura_linhas(_df_series(1), "mes", "n", None, "t", "r")
    assert fig.data[0].marker.symbol == "circle"
