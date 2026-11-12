import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from painel import componentes
from painel.dados import carregar_manifesto, total_processos
from painel.exibicao import formatar_inteiro, formatar_pct, texto_mediana

serie = componentes.serie_selecionada()

st.title("O que os metadados públicos do Datajud mostram sobre a judicialização "
         "da violência contra a mulher no Paraná")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.subheader("Mostra")
        st.write("Volume, enquadramento, tempos e desfechos de processos públicos de 1º grau do TJPR, "
                 "ajuizados de 2019 a 2026.")
with col2:
    with st.container(border=True):
        st.subheader(":red[●] Não mostra")
        st.write("Vítimas, incidência da violência, processos sigilosos, boletins de ocorrência, "
                 "dados de saúde.")


def _dias(v):
    return "1 dia" if int(round(float(v))) == 1 else f"{formatar_inteiro(v)} dias"


def _mediana(tabela, marco, tipo):
    t = tabela
    linha = t[(t["marco"] == marco) & (t["tipo_procedimento"] == tipo) & (t["serie"] == serie)
              & (t["estrato"] == "total")]
    if not len(linha):
        return "—", ""
    l = linha.iloc[0]
    ic = ""
    if l["estimavel"] and l["mediana_alcancada"]:
        ic = f" IC 95%: {formatar_inteiro(l['ic95_inf'])}–{formatar_inteiro(l['ic95_sup'])} dias."
        return _dias(l["mediana_dias"]), ic
    return texto_mediana(l), ic


tempo = componentes.tabela("agg_tempo")
desf = componentes.tabela("agg_desfecho")
sel = desf[(desf["tipo_procedimento"] == "ACAO_PENAL") & (desf["serie"] == serie)
           & (desf["variante"] == "principal") & (desf["estrato"] == "coorte")
           & (desf["valor_estrato"] == "2019-2021") & (desf["desfecho"] == "CONDENACAO")]
condenacao = "—"
if len(sel):
    linha = sel.iloc[0]
    if linha["suprimido"]:
        condenacao = "suprimido"
    elif not linha["estimavel"] or pd.isna(linha["ia_1825"]):
        condenacao = "não estimável"
    else:
        condenacao = formatar_pct(linha["ia_1825"], 0)

v_mpu, ic_mpu = _mediana(tempo, "decisao_mpu", "MPU")
v_sent, ic_sent = _mediana(tempo, "sentenca", "ACAO_PENAL")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Processos na base", formatar_inteiro(total_processos()),
          help="Processos na base analítica. São 147.002 registros coletados, contra 147.020 "
               "processos na base: a diferença de 18 corresponde a registros de 2026 que saíram "
               "do índice público entre as coletas.")
m2.metric("Mediana até decisão da MPU", v_mpu,
          help="Tempo mediano entre o ajuizamento e a decisão da medida protetiva (MPU)." + ic_mpu)
m3.metric("Mediana até a sentença", v_sent,
          help="Ações penais: tempo mediano entre o ajuizamento e a sentença." + ic_sent)
m4.metric("Condenação em 5 anos", condenacao,
          help="Ações penais ajuizadas de 2019 a 2021 (coorte): proporção com condenação até "
               "5 anos após o ajuizamento.")

cob = componentes.tabela("agg_cobertura_cnj")
vd = cob[(cob["medida"] == "vd_criterio_cnj") & cob["ano_ajuizamento"].between(2020, 2025)]["pct"].dropna()
man = carregar_manifesto()
st.caption(
    f"Nos anos completos de 2020 a 2025, a base pública reúne entre {formatar_pct(vd.min())} e "
    f"{formatar_pct(vd.max())} dos casos novos de violência doméstica informados pelo painel do CNJ "
    f"(mesmos critérios). Data de corte: {man['data_corte_max']}. "
    f"Versão das regras: {man['versao_regras']}. Unidade: processos públicos."
)
