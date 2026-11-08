import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from painel import componentes
from painel.exibicao import rotulo_ano
from painel.graficos import figura_barras, figura_linhas
from painel.rotulos import CATEGORIA, TIPO_PROCEDIMENTO
from painel.territorio import NOMES_MESORREGIAO

serie = componentes.serie_selecionada()
UNID = "processos públicos"

st.title("Volume no tempo")
st.caption("2026 é parcial: ajuizamentos até 30/09/2026, com setembro incompleto. "
           "2019 é tratado como ano de sensibilidade (a referência do CNJ para esse ano vem de outro "
           "produto e pode seguir critério diferente).")

tipos = st.multiselect("Tipos de procedimento", list(TIPO_PROCEDIMENTO), default=list(TIPO_PROCEDIMENTO),
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
st.plotly_chart(fig, use_container_width=True)
if vol["suprimido"].any():
    st.caption("Meses com valores suprimidos aparecem como pontos ausentes na série.")
componentes.rodape("Número de processos públicos ajuizados em cada mês.", "agg_volume.csv", serie)
componentes.botao_download(vol[["ano_ajuizamento", "mes_ajuizamento", "tipo_procedimento", "n", "suprimido"]],
                           "volume_mensal.csv")

# (b) jan-ago
st.subheader("Comparação jan–ago entre anos")
ja = componentes.tabela("agg_volume_jan_ago")
ja = ja[(ja["serie"] == serie) & ja["tipo_procedimento"].isin(tipos)].copy()
ja["ano"] = [rotulo_ano(int(a), int(a) == 2026) for a in ja["ano_ajuizamento"]]
if ja["suprimido"].any():
    st.caption("Há valores suprimidos no recorte: a soma não é apresentada; a contagem aparece por mesorregião.")
    nomes = NOMES_MESORREGIAO()
    ja["mesorregião"] = ja["mesorregiao_id"].map(lambda m: nomes.get(int(m), str(m)))
    exib = ja.groupby(["ano", "mesorregião"], sort=True, as_index=False).agg(
        n=("n", lambda s: s.sum(min_count=1)), suprimido=("suprimido", "any"))
    fig_b = figura_barras(exib, "ano", "n", "mesorregião", "Comparação jan–ago entre anos", UNID)
else:
    exib = ja.groupby("ano", sort=True, as_index=False).agg(n=("n", "sum"))
    exib["suprimido"] = False
    fig_b = figura_barras(exib, "ano", "n", None, "Comparação jan–ago entre anos", UNID)
componentes.grafico_ou_aviso(fig_b)
componentes.rodape("Processos ajuizados de janeiro a agosto, para comparar anos no mesmo intervalo de meses.",
                   "agg_volume_jan_ago.csv", serie)
componentes.botao_download(exib, "volume_jan_ago.csv")

# (c) categorias
st.subheader("Categorias de violência por ano")
st.warning("As categorias se sobrepõem: um processo pode ter mais de uma, e as barras não somam o total.")
cat = componentes.tabela("agg_categoria")
tipo_cat = st.selectbox("Tipo de procedimento (categorias)", list(TIPO_PROCEDIMENTO),
                        index=list(TIPO_PROCEDIMENTO).index("ACAO_PENAL"), format_func=TIPO_PROCEDIMENTO.get,
                        key="volume_cat_tipo")
cat = cat[(cat["serie"] == serie) & (cat["tipo_procedimento"] == tipo_cat)].copy()
g = cat.groupby(["ano_ajuizamento", "categoria"], as_index=False).agg(
    n=("n", lambda s: s.sum(min_count=1)), suprimido=("suprimido", "any"))
g["ano"] = [rotulo_ano(int(a), int(a) == 2026) for a in g["ano_ajuizamento"]]
g["categoria_nome"] = g["categoria"].map(CATEGORIA)
if g["suprimido"].any():
    st.caption("Combinações de ano e categoria com algum valor suprimido são omitidas, "
               "para que não se apresente uma soma incompleta (a soma entre mesorregiões só é feita quando nenhuma está suprimida).")
g = g.sort_values(["ano_ajuizamento", "categoria_nome"])
componentes.grafico_ou_aviso(figura_barras(g, "ano", "n", "categoria_nome",
                                           "Processos públicos por categoria e ano", UNID))
componentes.rodape("Processos por categoria de violência; categorias sobrepostas.",
                   "agg_categoria.csv", serie)
componentes.botao_download(g[["ano_ajuizamento", "categoria", "n", "suprimido"]], "volume_categoria.csv")
