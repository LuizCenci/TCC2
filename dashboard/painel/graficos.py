"""Construtores de figuras Plotly com o tema lilás."""
import pandas as pd
import plotly.graph_objects as go

from painel.exibicao import formatar_inteiro, formatar_pct
from painel.rotulos import DESFECHO

COR_PRINCIPAL = "#6A3D9A"
PALETA_CATEGORICA = ["#6A3D9A", "#9E9AC8", "#3F007D", "#BCBDDC",
                     "#807DBA", "#54278F", "#DADAEB", "#2D004B"]
ESCALA_SEQUENCIAL = ["#F2F0F7", "#DADAEB", "#BCBDDC", "#9E9AC8",
                     "#807DBA", "#6A51A3", "#4A1486"]
COR_SUPRIMIDO = "#BDBDBD"


def _layout(fig: go.Figure, titulo: str, rotulo_y: str | None = None) -> go.Figure:
    fig.update_layout(template="plotly_white", title=titulo, separators=",.",
                      font={"size": 14}, yaxis_title=rotulo_y, legend_title_text="")
    return fig


def _valores(serie: pd.Series, suprimido: pd.Series) -> list:
    return [None if s or pd.isna(v) else int(v) if float(v).is_integer() else float(v)
            for v, s in zip(serie, suprimido.fillna(False).astype(bool))]


def _grupos(df: pd.DataFrame, cor: str | None):
    if cor is None:
        yield None, df
    else:
        for nome, g in df.groupby(cor, sort=False):
            yield nome, g


def figura_linhas(df, x, y, cor, titulo, rotulo_y) -> go.Figure:
    fig = go.Figure()
    for i, (nome, g) in enumerate(_grupos(df, cor)):
        ys = _valores(g[y], g["suprimido"])
        textos = [formatar_inteiro(v) if v is not None else "suprimido" for v in ys]
        fig.add_trace(go.Scatter(
            x=list(g[x]), y=ys, mode="lines+markers", connectgaps=False,
            name=str(nome) if nome is not None else rotulo_y,
            line={"color": COR_PRINCIPAL if cor is None
                  else PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)]},
            text=textos, hovertemplate="%{x}: %{text}<extra>%{fullData.name}</extra>"))
    return _layout(fig, titulo, rotulo_y)


def figura_barras(df, x, y, cor, titulo, rotulo_y, horizontal=False):
    visiveis = df[~df["suprimido"].fillna(False).astype(bool) & df[y].notna()]
    if visiveis.empty:
        return None
    fig = go.Figure()
    for i, (nome, g) in enumerate(_grupos(visiveis, cor)):
        xs, ys = list(g[x]), _valores(g[y], g["suprimido"])
        textos = [formatar_inteiro(v) for v in ys]
        cor_barra = COR_PRINCIPAL if cor is None else PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)]
        fig.add_trace(go.Bar(
            x=ys if horizontal else xs, y=xs if horizontal else ys,
            orientation="h" if horizontal else "v",
            name=str(nome) if nome is not None else rotulo_y,
            marker={"color": cor_barra}, text=textos,
            hovertemplate="%{text}<extra>%{fullData.name}</extra>"))
    _layout(fig, titulo, None if horizontal else rotulo_y)
    if horizontal:
        fig.update_layout(xaxis_title=rotulo_y, yaxis_title=None)
    return fig


def figura_incidencia(df_desfecho) -> go.Figure:
    anos = {1: "ia_365", 2: "ia_730", 3: "ia_1095", 5: "ia_1825"}
    fig = go.Figure()
    for i, (_, linha) in enumerate(df_desfecho.iterrows()):
        ys = [None if pd.isna(linha[c]) else float(linha[c]) for c in anos.values()]
        fig.add_trace(go.Scatter(
            x=list(anos), y=ys, mode="lines+markers", name=DESFECHO.get(linha.get("desfecho"), str(linha.get("desfecho", i))),
            line={"color": PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)]},
            text=[formatar_pct(v) for v in ys],
            hovertemplate="%{x} ano(s): %{text}<extra>%{fullData.name}</extra>"))
    _layout(fig, "Incidência acumulada", "% de processos")
    fig.update_yaxes(rangemode="tozero")
    fig.update_layout(xaxis={"title": "anos desde o ajuizamento", "tickvals": list(anos)})
    return fig
