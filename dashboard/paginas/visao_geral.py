import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from painel import componentes
from painel.dados import carregar_manifesto, total_processos
from painel.exibicao import formatar_inteiro, formatar_pct, texto_mediana

serie = componentes.serie_selecionada()

st.title("O que os metadados públicos do Datajud mostram sobre a judicialização "
         "da violência contra a mulher no Paraná")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Mostra")
    st.write("Volume, enquadramento, tempos e desfechos de processos públicos de 1º grau do TJPR, "
             "ajuizados de 2019 a 2026.")
with col2:
    st.subheader("Não mostra")
    st.write("Vítimas, incidência da violência, processos sigilosos, boletins de ocorrência, "
             "dados de saúde.")


def _mediana(tabela, marco, tipo):
    t = tabela
    linha = t[(t["marco"] == marco) & (t["tipo_procedimento"] == tipo) & (t["serie"] == serie)
              & (t["estrato"] == "total")]
    return texto_mediana(linha.iloc[0]) if len(linha) else "—"


tempo = componentes.tabela("agg_tempo")
desf = componentes.tabela("agg_desfecho")
sel = desf[(desf["tipo_procedimento"] == "ACAO_PENAL") & (desf["serie"] == serie)
           & (desf["variante"] == "principal") & (desf["estrato"] == "coorte")
           & (desf["valor_estrato"] == "2019-2021") & (desf["desfecho"] == "CONDENACAO")]
condenacao = "—"
if len(sel):
    linha = sel.iloc[0]
    condenacao = "suprimido" if linha["suprimido"] else formatar_pct(linha["ia_1825"], 0)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Processos na base analítica", formatar_inteiro(total_processos()),
          help="147.002 registros coletados, contra 147.020 processos na base: a diferença de 18 "
               "corresponde a registros de 2026 que saíram do índice público entre as coletas.")
m2.metric("Mediana até a decisão da MPU", _mediana(tempo, "decisao_mpu", "MPU"))
m3.metric("Mediana até a sentença (ação penal)", _mediana(tempo, "sentenca", "ACAO_PENAL"))
m4.metric("Condenação em 5 anos (ajuizados 2019–2021)", condenacao)

cob = componentes.tabela("agg_cobertura_cnj")
mpu = cob[cob["medida"] == "mpu"]["pct"].dropna()
man = carregar_manifesto()
st.caption(
    f"O acervo público reúne de {formatar_pct(mpu.min())} a {formatar_pct(mpu.max())} das medidas "
    f"protetivas registradas nos painéis do CNJ. Data de corte: {man['data_corte_max']}. "
    f"Versão das regras: {man['versao_regras']}. Unidade: processos públicos."
)
