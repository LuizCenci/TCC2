import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from painel.dados import ErroIntegridade, verificar_integridade
from painel.rotulos import SERIE

st.set_page_config(page_title="Judicialização da violência contra a mulher no PR", layout="wide")

try:
    verificar_integridade()
except ErroIntegridade as erro:
    st.error(f"Os dados publicados não passaram na conferência de integridade: {erro}. "
             "Nenhum número é exibido.")
    st.stop()

with st.sidebar:
    st.radio(
        "Série", options=list(SERIE), format_func=SERIE.get, key="serie",
        help=("Estrita: critérios mais restritos de classificação do tipo de procedimento. "
              "Ampliada: inclui casos ambíguos adicionais. Vale para todas as páginas."),
    )
    st.caption("Estrita é o padrão; a ampliada mostra a sensibilidade ao critério.")

paginas = [
    st.Page("paginas/visao_geral.py", title="Visão geral", default=True),
    st.Page("paginas/volume.py", title="Volume no tempo"),
    st.Page("paginas/territorio.py", title="Território"),
    st.Page("paginas/mpu.py", title="Medidas protetivas"),
    st.Page("paginas/acoes_penais.py", title="Ações penais"),
    st.Page("paginas/cobertura.py", title="Cobertura e qualidade"),
    st.Page("paginas/sobre.py", title="Sobre os dados"),
]
st.navigation(paginas).run()
