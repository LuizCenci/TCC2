import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from painel import componentes
from painel.exibicao import MSG_TUDO_SUPRIMIDO, formatar_decimal, formatar_inteiro, texto_mediana, valor_ou_suprimido
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
titulo = f"{TIPO_PROCEDIMENTO[tipo]}, {ano}: {ROTULO_TAXA}"
if ano == 2026:
    st.caption("2026 é parcial (ajuizamentos até 30/09/2026); a taxa não é comparável com anos completos.")
if ano == 2019:
    st.caption("2019 é ano de sensibilidade: a referência do CNJ para esse ano pode seguir critério diferente.")

if not len(rec):
    st.info("Sem dados para este recorte.")
elif rec["suprimido"].all():
    st.info(MSG_TUDO_SUPRIMIDO)
st.plotly_chart(figura_mapa(rec, coluna, titulo), use_container_width=True)
if rec["suprimido_parcial"].any():
    st.caption("Há subcontagens ocultas em parte do recorte.")

rank = rec.copy()
rank["mesorregião"] = rank["mesorregiao_id"].map(lambda m: nomes.get(int(m), str(m)))
vis = rank[~rank["suprimido"] & rank[coluna].notna()].sort_values(coluna, ascending=False)
fig = figura_barras(vis, "mesorregião", coluna, None, "Ranking das mesorregiões", ROTULO_TAXA, horizontal=True)
if fig is not None:
    fig.update_traces(text=[formatar_decimal(v) for v in vis[coluna]])
    fig.update_yaxes(categoryorder="array", categoryarray=list(vis["mesorregião"])[::-1])
if len(rec) and not rec["suprimido"].all():
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
st.dataframe(tab, hide_index=True, use_container_width=True)
componentes.rodape(f"Taxa de {ROTULO_TAXA}; a suavizada é bayesiana empírica e não pode ser somada "
                   "entre anos ou tipos.", "agg_taxa.csv", serie)
componentes.botao_download(rec, "territorio_taxa.csv")

# tempos medianos
st.subheader("Tempos medianos por mesorregião")
marco = st.selectbox("Marco", list(MARCO), format_func=MARCO.get, key="territorio_marco")
tempo = componentes.tabela("agg_tempo")
t = tempo[(tempo["marco"] == marco) & (tempo["serie"] == serie)
          & (tempo["estrato"] == "mesorregiao_id")].copy()
if t.empty:
    st.info("Sem dados para este marco.")
else:
    t["Mesorregião"] = t["valor_estrato"].map(lambda v: nomes.get(int(v), str(v)))
    t["Tempo mediano"] = ["suprimido" if r["suprimido"] else texto_mediana(r) for _, r in t.iterrows()]
    t["Processos (n, arredondado)"] = [valor_ou_suprimido(r["n"], r["suprimido"]) for _, r in t.iterrows()]
    st.dataframe(t[["Mesorregião", "Tempo mediano", "Processos (n, arredondado)"]],
                 hide_index=True, use_container_width=True)
    componentes.rodape("Tempo mediano entre o ajuizamento e o marco; contagens arredondadas na base 10.",
                       "agg_tempo.csv", serie)
    componentes.botao_download(t[["marco", "valor_estrato", "n", "estimavel", "mediana_dias",
                                  "mediana_alcancada", "suprimido"]], "territorio_tempo.csv")
