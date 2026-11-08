import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from painel import componentes
from painel.exibicao import formatar_decimal, formatar_inteiro, formatar_pct, rotulo_ano
from painel.graficos import COR_PRINCIPAL, PALETA_CATEGORICA, _layout
from painel.rotulos import MEDIDA_COBERTURA

st.title("Cobertura e qualidade")
st.caption("Esta página compara contagens de registros entre duas fontes e descreve a qualidade dos dados. "
           "Não mede a cobertura exata da base pública.")

# (a) cobertura
st.subheader("Base pública e painel do CNJ")
st.markdown("A razão base pública / CNJ é a razão entre duas contagens de registros, de fontes e critérios "
            "diferentes. Não é cobertura exata nem taxa de judicialização.")
st.info("2019 é anômalo: a referência do CNJ para esse ano vem de outro produto, com critério possivelmente "
           "diferente, e o ano é tratado como de sensibilidade (feminicídio chega a 115%).")
cob = componentes.tabela("agg_cobertura_cnj").sort_values(["medida", "ano_ajuizamento"])
tab = pd.DataFrame({
    "Ano": [rotulo_ano(int(a), bool(p)) for a, p in zip(cob["ano_ajuizamento"], cob["ano_parcial"])],
    "Medida": cob["medida"].map(MEDIDA_COBERTURA),
    "Base pública": [formatar_inteiro(v) for v in cob["n_base"]],
    "Painel CNJ": [formatar_inteiro(v) for v in cob["n_cnj"]],
    "Razão base pública / CNJ (%)": [formatar_pct(v) for v in cob["pct"]],
})
st.dataframe(tab, hide_index=True, use_container_width=True)

fig = go.Figure()
for i, (medida, g) in enumerate(cob.groupby("medida", sort=False)):
    fig.add_trace(go.Bar(
        x=[rotulo_ano(int(a), bool(p)) for a, p in zip(g["ano_ajuizamento"], g["ano_parcial"])],
        y=[None if pd.isna(v) else float(v) for v in g["pct"]], name=MEDIDA_COBERTURA[medida],
        marker={"color": PALETA_CATEGORICA[i % len(PALETA_CATEGORICA)]},
        text=[formatar_pct(v) for v in g["pct"]],
        hovertemplate="%{x}: %{text}<extra>%{fullData.name}</extra>"))
_layout(fig, "Razão base pública / CNJ (%) por ano e medida", "razão entre contagens de registros (%)")
fig.update_layout(barmode="group")
st.plotly_chart(fig, use_container_width=True)
componentes.rodape("Contagem da base pública dividida pela contagem do painel do CNJ, por ano de ajuizamento "
                   "e medida; razão entre registros, não cobertura exata.", "agg_cobertura_cnj.csv")
componentes.botao_download(cob[["ano_ajuizamento", "medida", "n_base", "n_cnj", "pct"]], "cobertura_cnj.csv")

# (b) qualidade por órgão
st.subheader("Qualidade por órgão julgador")
q = componentes.tabela("agg_qualidade_orgao")
vis = q[~q["suprimido"]]
st.caption(f"{len(vis)} de {len(q)} órgãos têm valores visíveis; os demais estão suprimidos para proteger a "
           "privacidade e não entram nos gráficos. Os órgãos não são listados por nome.")
if vis.empty:
    st.info("Todos os valores deste recorte foram suprimidos para proteger a privacidade.")
else:
    h1 = go.Figure(go.Histogram(x=vis["mediana_movimentos"].dropna(), marker={"color": COR_PRINCIPAL}, nbinsx=20,
                                hovertemplate="%{x}: %{y} órgãos<extra></extra>"))
    _layout(h1, "Mediana de movimentos por processo, por órgão", "órgãos")
    h1.update_layout(xaxis_title="mediana de movimentos por processo")
    st.plotly_chart(h1, use_container_width=True)
    dup = vis["n_processos_com_duplicado"].dropna()
    if len(dup):
        h2 = go.Figure(go.Histogram(x=dup, marker={"color": COR_PRINCIPAL}, nbinsx=20,
                                    hovertemplate="%{x}: %{y} órgãos<extra></extra>"))
        _layout(h2, "Processos com movimento duplicado, por órgão", "órgãos")
        h2.update_layout(xaxis_title="processos públicos com movimento duplicado")
        st.plotly_chart(h2, use_container_width=True)
    if vis["suprimido_parcial"].any():
        st.caption("Em alguns órgãos, a contagem de processos com movimento duplicado está oculta; "
                   "esses órgãos não entram no segundo gráfico.")
    st.caption(f"Mediana das medianas de movimentos: {formatar_decimal(vis['mediana_movimentos'].median())}.")
componentes.rodape("Distribuição, entre órgãos não suprimidos, da mediana de movimentos por processo e "
                   "do número de processos com movimento duplicado.", "agg_qualidade_orgao.csv")
_q = vis[["orgao_codigo", "mesorregiao_id", "orgao_especializado", "n", "media_movimentos",
          "mediana_movimentos", "n_processos_com_duplicado"]]
componentes.botao_download(_q, "qualidade_orgao.csv")
