"""Mapa coroplético das mesorregiões do Paraná."""
import pandas as pd
import plotly.graph_objects as go

from painel.exibicao import formatar_decimal
from painel.graficos import COR_SUPRIMIDO, ESCALA_SEQUENCIAL
from painel.territorio import NOMES_MESORREGIAO, carregar_mesorregioes


def figura_mapa(df_taxa, coluna_valor: str, titulo: str) -> go.Figure:
    nomes = NOMES_MESORREGIAO()
    linhas = {int(r["mesorregiao_id"]): r for _, r in df_taxa.iterrows()}
    cinza, valores = [], []
    for mid in sorted(nomes):
        r = linhas.get(mid)
        if r is None:
            cinza.append((mid, "sem dado"))
        elif (not pd.isna(r.get("suprimido", False)) and bool(r.get("suprimido", False))) or pd.isna(r[coluna_valor]):
            cinza.append((mid, "suprimido"))
        else:
            valores.append((mid, float(r[coluna_valor])))
    geo = carregar_mesorregioes()
    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        geojson=geo, featureidkey="properties.mesorregiao_id",
        locations=[m for m, _ in cinza], z=[0] * len(cinza),
        colorscale=[[0, COR_SUPRIMIDO], [1, COR_SUPRIMIDO]], showscale=False,
        text=[f"{nomes[m]}: {t}" for m, t in cinza], hoverinfo="text"))
    fig.add_trace(go.Choropleth(
        geojson=geo, featureidkey="properties.mesorregiao_id",
        locations=[m for m, _ in valores], z=[v for _, v in valores],
        colorscale=[[i / (len(ESCALA_SEQUENCIAL) - 1), c] for i, c in enumerate(ESCALA_SEQUENCIAL)],
        text=[f"{nomes[m]}: {formatar_decimal(v)}" for m, v in valores], hoverinfo="text",
        colorbar={"title": ""}))
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(template="plotly_white", title=titulo, separators=",.",
                      font={"size": 14}, margin={"l": 0, "r": 0, "t": 50, "b": 0})
    return fig
