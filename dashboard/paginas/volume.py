import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from painel import componentes
from painel.exibicao import rotulo_ano
from painel.graficos import figura_barras, figura_linhas
from painel.rotulos import CATEGORIA, TIPO_PROCEDIMENTO

serie = componentes.serie_selecionada()
UNID = "processos públicos"

st.title("Volume no tempo")
st.caption("2026 é parcial: ajuizamentos até 30/09/2026, com setembro incompleto. "
           "2019 é tratado como ano de sensibilidade e não entra na comparação com o painel do CNJ.")

tipos = st.multiselect("Tipos de procedimento", list(TIPO_PROCEDIMENTO), default=["ACAO_PENAL", "INQUERITO", "MPU"],
                       format_func=TIPO_PROCEDIMENTO.get, key="volume_tipos")
if not tipos:
    st.info("Selecione ao menos um tipo de procedimento.")
    st.stop()

# (a) série mensal
vol = componentes.tabela("agg_volume")
vol = vol[(vol["serie"] == serie) & vol["tipo_procedimento"].isin(tipos)].copy()
vol["data"] = [pd.Timestamp(int(a), int(m), 1) for a, m in zip(vol["ano_ajuizamento"], vol["mes_ajuizamento"])]
vol["tipo"] = vol["tipo_procedimento"].map(TIPO_PROCEDIMENTO)
vol = vol.sort_values(["tipo", "data"])
st.subheader("Série mensal por tipo de procedimento")
fig = figura_linhas(vol, "data", "n", "tipo", "Processos públicos ajuizados por mês", UNID)
fig.update_xaxes(tickformat="%Y-%m")
fig.add_vrect(x0="2026-01-01", x1="2026-09-30", fillcolor="#BDBDBD", opacity=0.2, line_width=0,
              annotation_text="2026 parcial", annotation_position="top left")
st.plotly_chart(fig, width="stretch")
if vol["suprimido"].any():
    st.caption("Meses com valores suprimidos aparecem como pontos ausentes na série.")
componentes.rodape("Número de processos públicos ajuizados em cada mês.", "agg_volume.csv", serie)
_v = vol[["ano_ajuizamento", "mes_ajuizamento", "tipo_procedimento", "n", "suprimido"]].copy()
_v["n"] = _v["n"].mask(_v["suprimido"], pd.NA)
componentes.botao_download(_v, "volume_mensal.csv")

# (b) jan-ago, calculado a partir da série mensal estadual
st.subheader("Comparação jan–ago entre anos")
base = componentes.tabela("agg_volume")
base = base[(base["serie"] == serie) & base["tipo_procedimento"].isin(tipos) & base["mes_ajuizamento"].between(1, 8)]
linhas, omitidos = [], []
for (ano_, tp), g_ in base.groupby(["ano_ajuizamento", "tipo_procedimento"]):
    if len(g_) < 8 or g_["suprimido"].any() or g_["n"].isna().any():
        omitidos.append(f"{rotulo_ano(int(ano_), int(ano_) == 2026)} / {TIPO_PROCEDIMENTO[tp]}")
        continue
    linhas.append({"ano": rotulo_ano(int(ano_), int(ano_) == 2026), "ano_ajuizamento": int(ano_),
                   "tipo": TIPO_PROCEDIMENTO[tp], "n": int(g_["n"].sum()), "suprimido": False})
exib = pd.DataFrame(linhas, columns=["ano", "ano_ajuizamento", "tipo", "n", "suprimido"])
exib = exib.sort_values(["ano_ajuizamento", "tipo"])
fig_b = figura_barras(exib, "ano", "n", "tipo", "Comparação jan–ago entre anos", UNID)
if fig_b is not None:
    fig_b.update_layout(barmode="group")
    fig_b.update_xaxes(categoryorder="array",
                       categoryarray=[rotulo_ano(a_, a_ == 2026) for a_ in range(2019, 2027)])
componentes.grafico_ou_aviso(fig_b)
if omitidos:
    st.caption("Combinações suprimidas (barra não desenhada, sem soma parcial): " + "; ".join(omitidos) + ".")
componentes.rodape("Processos ajuizados de janeiro a agosto (soma dos meses 1 a 8 da série mensal), "
                   "para comparar anos no mesmo intervalo de meses.", "agg_volume.csv", serie)
componentes.botao_download(exib[["ano_ajuizamento", "tipo", "n"]], "volume_jan_ago.csv")

# (c) categorias
st.subheader("Categorias de violência por ano")
st.warning("As categorias se sobrepõem: um processo pode ter mais de uma, e as barras não somam o total.")
cat = componentes.tabela("agg_cautelar")
tipo_cat = st.selectbox("Tipo de procedimento (categorias)", list(TIPO_PROCEDIMENTO),
                        index=list(TIPO_PROCEDIMENTO).index("ACAO_PENAL"), format_func=TIPO_PROCEDIMENTO.get,
                        key="volume_cat_tipo")
g = cat[(cat["serie"] == serie) & (cat["tipo_procedimento"] == tipo_cat)].copy()
g["ano"] = [rotulo_ano(int(a), int(a) == 2026) for a in g["ano_ajuizamento"]]
g["categoria_nome"] = g["categoria"].map(CATEGORIA)
sup = g[g["suprimido"] | g["n"].isna()]
if len(sup):
    st.caption("Combinações suprimidas: " + "; ".join(
        f"{a} / {c}" for a, c in zip(sup["ano"], sup["categoria_nome"])) + ".")
g = g.sort_values(["ano_ajuizamento", "categoria_nome"])
fig_c = figura_barras(g, "ano", "n", "categoria_nome", "Processos públicos por categoria e ano", UNID)
if fig_c is not None:
    fig_c.update_xaxes(categoryorder="array",
                       categoryarray=[rotulo_ano(a_, a_ == 2026) for a_ in range(2019, 2027)])
componentes.grafico_ou_aviso(fig_c)
componentes.rodape("Contagem de processos por categoria de violência no estado, por ano de ajuizamento; "
                   "categorias sobrepostas.", "agg_cautelar.csv", serie)
_g = g[["ano_ajuizamento", "categoria", "n", "suprimido"]].copy()
_g["n"] = _g["n"].mask(_g["suprimido"], pd.NA)
componentes.botao_download(_g, "volume_categoria.csv")
