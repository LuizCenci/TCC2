import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from painel import componentes
from painel.exibicao import MSG_TUDO_SUPRIMIDO, colunas_tempo, formatar_pct, rotulo_ano, texto_mediana
from painel.graficos import figura_barras, figura_linhas
from painel.rotulos import rotulo_medida

serie = componentes.serie_selecionada()
UNID = "processos públicos"

st.title("Medidas protetivas")
st.caption("2026 é parcial: ajuizamentos até 30/09/2026, com setembro incompleto. "
           "Decisão genérica ou ausência de evento não comprova concessão ou indeferimento.")

# (a) decisões por ano
st.subheader("Decisões e revogações por ano de ajuizamento")
filtro = st.selectbox("Órgão especializado", ["todos", "sim", "não"], key="mpu_orgao")
mpu = componentes.tabela("agg_mpu")
mpu = mpu[mpu["serie"] == serie].copy()
if filtro != "todos":
    mpu = mpu[mpu["orgao_especializado"] == (filtro == "sim")]
COLS = ["n_com_decisao", "n_deferimento", "n_parcial", "n_indeferimento", "n_revogadas"]
linhas, omitidos = [], []
for ano_, g in mpu.groupby("ano_ajuizamento"):
    rot = rotulo_ano(int(ano_), int(ano_) == 2026)
    if g["suprimido"].any() or g[COLS].isna().any().any():
        omitidos.append(rot)
        continue
    linhas.append({"ano_ajuizamento": int(ano_), "ano": rot, "n": int(g["n"].sum()),
                   **{c: int(g[c].sum()) for c in COLS}})
dec = pd.DataFrame(linhas, columns=["ano_ajuizamento", "ano", "n"] + COLS).sort_values("ano_ajuizamento")
if dec.empty:
    st.info(MSG_TUDO_SUPRIMIDO)
else:
    long = dec.melt(id_vars=["ano_ajuizamento", "ano"],
                    value_vars=["n_deferimento", "n_parcial", "n_indeferimento"],
                    var_name="decisao", value_name="valor")
    long["decisão"] = long["decisao"].map({"n_deferimento": "Deferimento", "n_parcial": "Deferimento parcial",
                                           "n_indeferimento": "Indeferimento"})
    long["suprimido"] = False
    long = long.sort_values(["ano_ajuizamento", "decisão"])
    fig = figura_barras(long, "ano", "valor", "decisão",
                        "Decisões sobre o pedido de medida protetiva, entre os processos com decisão", UNID)
    fig.update_layout(barmode="stack")
    st.plotly_chart(fig, width="stretch")
    rev = dec.assign(suprimido=False)
    st.plotly_chart(figura_linhas(rev, "ano", "n_revogadas", None, "Medidas revogadas por ano", UNID),
                    width="stretch")
if omitidos:
    st.caption("Anos omitidos por supressão (sem soma parcial): " + "; ".join(omitidos) + ".")
componentes.rodape("Decisões entre processos de medida protetiva com decisão identificada nos movimentos; "
                   "revogações contadas à parte.", "agg_mpu.csv", serie)
componentes.botao_download(dec.drop(columns=["ano"]), "mpu_decisoes.csv")

# (b) tempo até a decisão
st.subheader("Tempo até a decisão da medida protetiva")
tempo = componentes.tabela("agg_tempo")
t = tempo[(tempo["marco"] == "decisao_mpu") & (tempo["serie"] == serie)]
tot = t[t["estrato"] == "total"]
if len(tot) and not tot.iloc[0]["suprimido"]:
    r = tot.iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mediana", texto_mediana(r).split(" (")[0])
    c2.metric("Até 2 dias", formatar_pct(r["pct_evento_ate_2"]))
    c3.metric("Até 30 dias", formatar_pct(r["pct_evento_ate_30"]))
    c4.metric("Até 365 dias", formatar_pct(r["pct_evento_ate_365"]))
    st.caption(f"Mediana com intervalo de confiança: {texto_mediana(r)}.")
else:
    st.info("Sem dado visível para o total do estado.")
ta = t[t["estrato"] == "ano_ajuizamento"].copy()
ta["_ano"] = ta["valor_estrato"].astype(int)
ta = ta.sort_values("_ano")
if len(ta):
    s = ta["suprimido"].astype(bool)
    tab = colunas_tempo(ta)
    tab.insert(0, "Ano de ajuizamento", [rotulo_ano(a, a == 2026) for a in ta["_ano"]])
    for rot, col in [("Até 2 dias (%)", "pct_evento_ate_2"), ("Até 30 dias (%)", "pct_evento_ate_30"),
                     ("Até 365 dias (%)", "pct_evento_ate_365")]:
        tab[rot] = ta[col].astype(float).mask(s)
    _nc = st.column_config.NumberColumn
    st.dataframe(tab, hide_index=True, width="stretch", column_config={
        "Mediana (dias)": _nc(format="localized"), "Processos (n, arredondado)": _nc(format="localized"),
        "Até 2 dias (%)": _nc(format="localized"), "Até 30 dias (%)": _nc(format="localized"),
        "Até 365 dias (%)": _nc(format="localized")})
componentes.rodape("Tempo entre o ajuizamento e a decisão da medida protetiva; percentuais de processos com "
                   "decisão no prazo; contagens arredondadas na base 10.", "agg_tempo.csv", serie)
_t = t[["estrato", "valor_estrato", "n", "estimavel", "mediana_dias", "mediana_alcancada", "ic95_inf", "ic95_sup",
        "pct_evento_ate_2", "pct_evento_ate_30", "pct_evento_ate_365", "suprimido"]].copy()
for c in ["n", "mediana_dias", "ic95_inf", "ic95_sup", "pct_evento_ate_2", "pct_evento_ate_30",
          "pct_evento_ate_365"]:
    _t[c] = _t[c].mask(_t["suprimido"], pd.NA)
componentes.botao_download(_t, "mpu_tempo_decisao.csv")

# (c) tipos de medida
st.subheader("Tipos de medida concedidos")
med = componentes.tabela("agg_mpu_medida")
ano_m = st.selectbox("Ano de ajuizamento (tipos de medida)", list(range(2019, 2027)), index=6,
                     format_func=lambda a: rotulo_ano(a, a == 2026), key="mpu_medida_ano")
m = med[med["ano_ajuizamento"] == ano_m]
visiveis = m[~m["suprimido"] & m["n"].notna()]
n_supr = int(m["suprimido"].sum())
res = visiveis.groupby("tipo_medida", as_index=False)["n"].sum()
res["medida"] = res["tipo_medida"].map(rotulo_medida)
res["suprimido"] = False
res = res.sort_values("n", ascending=False)
fig_m = figura_barras(res, "medida", "n", None, f"Tipos de medida, {rotulo_ano(ano_m, ano_m == 2026)}",
                      "mínimo (soma das mesorregiões não suprimidas)", horizontal=True)
if fig_m is not None:
    fig_m.update_yaxes(categoryorder="array", categoryarray=list(res["medida"])[::-1])
componentes.grafico_ou_aviso(fig_m)
st.caption(f"Os valores são um mínimo (soma das mesorregiões não suprimidas), não um total: "
           f"{n_supr} de {len(m)} linhas de mesorregião e tipo estão suprimidas e ficaram fora da soma. "
           "Nomes de medida truncados na fonte podem reunir medidas distintas.")
componentes.rodape("Medidas concedidas por tipo, somadas só sobre as mesorregiões não suprimidas.",
                   "agg_mpu_medida.csv")
componentes.botao_download(res[["tipo_medida", "n"]].rename(
    columns={"n": "n_minimo_mesorregioes_nao_suprimidas"}), "mpu_tipos_medida.csv")
