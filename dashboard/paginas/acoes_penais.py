import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from painel import componentes
from painel.exibicao import MSG_TUDO_SUPRIMIDO, formatar_inteiro, rotulo_ano, texto_mediana
from painel.graficos import figura_barras, figura_incidencia
from painel.rotulos import CATEGORIA, MARCO, TIPO_PROCEDIMENTO

serie = componentes.serie_selecionada()
UNID = "processos públicos"
COORTES = ["2019-2021", "2022-2023", "2024-2026"]
VARIANTES = {"principal": "Principal", "com_reativados": "Com processos reativados"}

st.title("Ações penais")
st.caption("2026 é parcial: ajuizamentos até 30/09/2026, com setembro incompleto. "
           "As contagens de tempos e desfechos estão arredondadas na base 10.")

tempo = componentes.tabela("agg_tempo")
desf = componentes.tabela("agg_desfecho")


def bloco_tempos(tipo: str, marcos: list[str], chave: str) -> None:
    for marco in marcos:
        t = tempo[(tempo["marco"] == marco) & (tempo["tipo_procedimento"] == tipo)
                  & (tempo["serie"] == serie)]
        if t.empty:
            continue
        st.markdown(f"**{MARCO[marco]}**")
        tot = t[t["estrato"] == "total"]
        if len(tot):
            r = tot.iloc[0]
            st.write("Total: " + ("suprimido" if r["suprimido"] else texto_mediana(r)))
        ta = t[t["estrato"] == "ano_ajuizamento"].copy()
        ta["_ano"] = ta["valor_estrato"].astype(int)
        ta = ta.sort_values("_ano")
        s = ta["suprimido"].tolist()
        st.dataframe(pd.DataFrame({
            "Ano de ajuizamento": [rotulo_ano(a, a == 2026) for a in ta["_ano"]],
            "Tempo mediano": ["suprimido" if x else texto_mediana(r) for x, (_, r) in zip(s, ta.iterrows())],
            "Processos (n, arredondado)": ["suprimido" if x else formatar_inteiro(v) for x, v in zip(s, ta["n"])],
        }), hide_index=True, width="stretch")
        componentes.rodape(f"Tempo mediano entre o ajuizamento e o marco ({MARCO[marco].lower()}), com IC 95%; "
                           "contagens arredondadas na base 10.", "agg_tempo.csv", serie)
        d = ta[["marco", "valor_estrato", "n", "estimavel", "mediana_dias", "mediana_alcancada",
                "ic95_inf", "ic95_sup", "suprimido"]].copy()
        for c in ["n", "mediana_dias", "ic95_inf", "ic95_sup"]:
            d[c] = d[c].mask(d["suprimido"], pd.NA)
        componentes.botao_download(d, f"{chave}_tempo_{marco}.csv")


def bloco_desfecho(tipo: str, chave: str) -> None:
    c1, c2 = st.columns(2)
    coorte = c1.selectbox("Coorte de ajuizamento", COORTES, index=0, key=f"{chave}_coorte")
    variante = c2.selectbox("Variante", list(VARIANTES), format_func=VARIANTES.get, key=f"{chave}_variante")
    d = desf[(desf["tipo_procedimento"] == tipo) & (desf["serie"] == serie) & (desf["variante"] == variante)
             & (desf["estrato"] == "coorte") & (desf["valor_estrato"] == coorte)].copy()
    if d.empty or d["suprimido"].all():
        st.info(MSG_TUDO_SUPRIMIDO if len(d) else "Sem dados para este recorte.")
        return
    if (~d["estimavel"]).any():
        st.caption("Desfechos não estimáveis foram omitidos do gráfico.")
    if d["suprimido"].any():
        st.caption("Desfechos suprimidos foram omitidos do gráfico.")
    vis = d[~d["suprimido"] & d["estimavel"]]
    if vis.empty:
        st.info("Nenhum desfecho estimável neste recorte.")
        return
    st.plotly_chart(figura_incidencia(vis), width="stretch")
    st.caption("Incidência acumulada: percentual de processos da coorte com o desfecho até 1, 2, 3 e 5 anos "
               "após o ajuizamento. Coortes recentes não têm 5 anos de acompanhamento.")
    componentes.rodape("Incidência acumulada de desfechos por coorte de ajuizamento; contagens arredondadas "
                       "na base 10.", "agg_desfecho.csv", serie)
    out = d[["tipo_procedimento", "variante", "valor_estrato", "desfecho", "n", "n_desfecho",
             "ia_365", "ia_730", "ia_1095", "ia_1825", "suprimido"]].copy()
    for c in ["n", "n_desfecho", "ia_365", "ia_730", "ia_1095", "ia_1825"]:
        out[c] = out[c].mask(out["suprimido"], pd.NA)
    componentes.botao_download(out, f"{chave}_desfecho.csv")


aba_ap, aba_inq = st.tabs(["Ações penais", "Inquéritos"])

with aba_ap:
    st.subheader("Tempos até o recebimento da denúncia e até a sentença")
    bloco_tempos("ACAO_PENAL", ["recebimento_denuncia", "sentenca"], "ap")
    st.subheader("Desfechos acumulados")
    bloco_desfecho("ACAO_PENAL", "ap")

    st.subheader("Resposta cautelar")
    caut = componentes.tabela("agg_cautelar")
    cc1, cc2 = st.columns(2)
    tipo_c = cc1.selectbox("Tipo de procedimento (cautelar)", ["ACAO_PENAL", "INQUERITO"],
                           format_func=TIPO_PROCEDIMENTO.get, key="ap_cautelar_tipo")
    cat_c = cc2.selectbox("Categoria (cautelar)", list(CATEGORIA), format_func=CATEGORIA.get,
                          key="ap_cautelar_cat")
    cd = caut[(caut["serie"] == serie) & (caut["tipo_procedimento"] == tipo_c) & (caut["categoria"] == cat_c)]
    cd = cd.sort_values("ano_ajuizamento")
    nomes = {"n_flagrante": "Prisão em flagrante", "n_preventiva": "Prisão preventiva",
             "n_liberdade_provisoria_concedida": "Liberdade provisória concedida"}
    long = cd.melt(id_vars=["ano_ajuizamento", "suprimido"], value_vars=list(nomes),
                   var_name="evento", value_name="valor")
    long["evento"] = long["evento"].map(nomes)
    long["ano"] = [rotulo_ano(int(a), int(a) == 2026) for a in long["ano_ajuizamento"]]
    fig = figura_barras(long, "ano", "valor", "evento",
                        f"Resposta cautelar, {TIPO_PROCEDIMENTO[tipo_c].lower()}, {CATEGORIA[cat_c].lower()}", UNID)
    if fig is not None:
        fig.update_layout(barmode="group")
        fig.update_xaxes(categoryorder="array",
                         categoryarray=[rotulo_ano(a_, a_ == 2026) for a_ in range(2019, 2027)])
    componentes.grafico_ou_aviso(fig)
    _vis = long[~long["suprimido"].astype(bool) & long["valor"].notna()]
    _sem = [rotulo_ano(a_, a_ == 2026) for a_ in range(2019, 2027)
            if a_ not in set(_vis["ano_ajuizamento"].astype(int))]
    if _sem:
        st.caption("Anos sem valor visível (suprimidos ou sem dados): " + "; ".join(_sem) + ".")
    if cd["suprimido_parcial"].any():
        st.caption("Há subcontagens ocultas em parte dos anos; valores ausentes não são zero.")
    componentes.rodape("Processos com o movimento indicado (flagrante, preventiva, liberdade provisória "
                       "concedida), por ano de ajuizamento.", "agg_cautelar.csv", serie)
    _c = long[["ano_ajuizamento", "evento", "valor", "suprimido"]].copy()
    _c["valor"] = _c["valor"].mask(_c["suprimido"], pd.NA)
    componentes.botao_download(_c, "ap_cautelar.csv")

with aba_inq:
    st.subheader("Tempo até o recebimento da denúncia")
    bloco_tempos("INQUERITO", ["recebimento_denuncia"], "inq")
    st.subheader("Desfechos acumulados")
    bloco_desfecho("INQUERITO", "inq")
