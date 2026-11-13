import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from painel import componentes
from painel.exibicao import rotulo_ano, MSG_TUDO_SUPRIMIDO, formatar_decimal, formatar_inteiro, colunas_tempo, valor_ou_suprimido
from painel.graficos import figura_barras
from painel.mapa import figura_mapa
from painel.rotulos import MARCO, TIPO_PROCEDIMENTO
from painel.territorio import NOMES_MESORREGIAO

serie = componentes.serie_selecionada()
ROTULO_TAXA = "processos públicos por 100 mil mulheres (Censo 2022)"
anos = list(range(2019, 2027))

st.title("Território")
c1, c2, c3 = st.columns(3)
ano = c1.selectbox("Ano", anos, index=anos.index(2025), key="territorio_ano",
                   format_func=lambda a: f"{a} (parcial)" if a == 2026 else str(a))
tipo = c2.selectbox("Tipo de procedimento", list(TIPO_PROCEDIMENTO),
                    index=list(TIPO_PROCEDIMENTO).index("ACAO_PENAL"),
                    key="territorio_tipo", format_func=TIPO_PROCEDIMENTO.get)
tipo_taxa = c3.radio("Taxa", ["Suavizada (bayesiana empírica)", "Bruta"], key="territorio_taxa")
coluna = "taxa_eb_100k" if tipo_taxa.startswith("Suavizada") else "taxa_bruta_100k"

st.warning("A localização é a do município-sede do órgão julgador, não a do fato nem a da residência da vítima.")

nomes = NOMES_MESORREGIAO()
taxa = componentes.tabela("agg_taxa")
rec = taxa[(taxa["serie"] == serie) & (taxa["ano_ajuizamento"] == ano)
           & (taxa["tipo_procedimento"] == tipo)].copy()
titulo = f"{TIPO_PROCEDIMENTO[tipo]}, {rotulo_ano(ano, ano == 2026)}: {ROTULO_TAXA}"
if ano == 2026:
    st.caption("2026 é parcial (ajuizamentos até 30/09/2026); a taxa não é comparável com anos completos.")
if ano == 2019:
    st.caption("2019 é ano de sensibilidade e não entra na comparação com o painel do CNJ.")

if not len(rec):
    st.info("Sem dados para este recorte.")
elif rec["suprimido"].all():
    st.info(MSG_TUDO_SUPRIMIDO)
st.plotly_chart(figura_mapa(rec, coluna, titulo), width="stretch")
if rec["suprimido_parcial"].any():
    st.caption("Há subcontagens ocultas em parte do recorte.")

rank = rec.copy()
rank["mesorregião"] = rank["mesorregiao_id"].map(lambda m: nomes.get(int(m), str(m)))
if len(rec) and not rec["suprimido"].all():
    vis = rank[~rank["suprimido"] & rank[coluna].notna()].sort_values(coluna, ascending=False)
    fig = figura_barras(vis, "mesorregião", coluna, None, "Ranking das mesorregiões", ROTULO_TAXA,
                        horizontal=True)
    if fig is not None:
        fig.update_traces(text=[formatar_decimal(v) for v in vis[coluna]])
        fig.update_yaxes(categoryorder="array", categoryarray=list(vis["mesorregião"])[::-1])
    componentes.grafico_ou_aviso(fig)

tab = pd.DataFrame({
    "Mesorregião": rank["mesorregião"],
    "Processos públicos (n)": [valor_ou_suprimido(n, s) for n, s in zip(rank["n"], rank["suprimido"])],
    "População feminina": [formatar_inteiro(p) for p in rank["pop_feminina"]],
    "Taxa bruta": [valor_ou_suprimido(v, s, formatar_decimal)
                   for v, s in zip(rank["taxa_bruta_100k"], rank["suprimido"])],
    "Taxa suavizada (EB)": [valor_ou_suprimido(v, s, formatar_decimal)
                            for v, s in zip(rank["taxa_eb_100k"], rank["suprimido"])],
})
st.dataframe(tab, hide_index=True, width="stretch")
componentes.rodape(f"Taxa de {ROTULO_TAXA}; a suavizada é bayesiana empírica e não pode ser somada "
                   "entre anos ou tipos.", "agg_taxa.csv", serie)
_r = rec.copy()
for _c in ["n", "taxa_bruta_100k", "taxa_eb_100k"]:
    _r[_c] = _r[_c].mask(_r["suprimido"], pd.NA)
componentes.botao_download(_r, "territorio_taxa.csv")

# tempos medianos
st.subheader("Tempos medianos por mesorregião")
tempo = componentes.tabela("agg_tempo")
_base = tempo[(tempo["serie"] == serie) & (tempo["tipo_procedimento"] == tipo)
              & (tempo["estrato"] == "mesorregiao_id")]
_disp = [m for m in MARCO if m in set(_base["marco"])]
if not _disp:
    st.info("Não há tempos calculados para este tipo de procedimento. Os tempos existem para ação penal, inquérito e medida protetiva de urgência.")
    t = _base.iloc[0:0].copy()
else:
    _padrao = "sentenca" if "sentenca" in _disp else ("decisao_mpu" if "decisao_mpu" in _disp else _disp[0])
    marco = st.selectbox("Marco", _disp, index=_disp.index(_padrao), format_func=MARCO.get,
                         key=f"territorio_marco_{tipo}")
    t = _base[_base["marco"] == marco].copy()
if t.empty:
    if _disp:
        st.info("Sem dados de tempo para este tipo de procedimento e marco.")
else:
    t["Mesorregião"] = t["valor_estrato"].map(lambda v: nomes.get(int(v), str(v)))
    _tab = colunas_tempo(t)
    _tab.insert(0, "Mesorregião", t["Mesorregião"])
    st.dataframe(_tab, hide_index=True, width="stretch", placeholder="", column_config={
        "Situação": st.column_config.TextColumn(width="large"),
        "Mediana (dias)": st.column_config.NumberColumn(format="localized"),
        "Processos (n, arredondado)": st.column_config.NumberColumn(format="localized")})
    componentes.rodape("Tempo mediano entre o ajuizamento e o marco; contagens arredondadas na base 10.",
                       "agg_tempo.csv", serie)
    st.caption("A tabela agrega todos os anos de ajuizamento e usa o tipo de procedimento selecionado acima.")
    _t = t[["tipo_procedimento", "marco", "valor_estrato", "n", "estimavel", "mediana_dias", "mediana_alcancada", "suprimido"]].copy()
    for _c in ["n", "mediana_dias"]:
        _t[_c] = _t[_c].mask(_t["suprimido"], pd.NA)
    componentes.botao_download(_t, "territorio_tempo.csv")
