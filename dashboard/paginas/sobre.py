import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from painel import componentes
from painel.dados import carregar_manifesto

st.title("Sobre os dados")

st.subheader("Fonte")
st.write("API Pública do Datajud, do Conselho Nacional de Justiça (CNJ).")

st.subheader("Recorte")
st.write("Tribunal de Justiça do Paraná (TJPR), 1º grau, ajuizamentos de 2019 a 2026, apenas processos "
         "públicos (`nivelSigilo` 0), com ajuizamentos até 30/09/2026. O ano de 2026 é parcial e "
         "aparece sempre assim rotulado.")

st.subheader("Pipeline")
st.write("Bronze (respostas originais da API) → Silver (dados normalizados) → Gold (agregações "
         "publicadas neste painel). Execuções registradas:")
pipe = componentes.tabela("agg_pipeline").drop(columns=["pergunta"], errors="ignore")
st.dataframe(pipe, hide_index=True, use_container_width=True)
man = carregar_manifesto()
st.caption(f"Versão das regras: {man['versao_regras']}. Data de corte: {man['data_corte_max']}.")

st.subheader("Regras de supressão")
st.markdown(
    "- Contagens com menos de 5 processos são suprimidas.\n"
    "- Por órgão julgador, o mínimo é de 10 processos.\n"
    "- Há supressão secundária, para que um valor suprimido não possa ser recuperado por diferença.\n"
    "- Contagens de tempos e desfechos são arredondadas na base 10."
)

st.subheader("Séries estrita e ampliada")
st.write("A série estrita usa critérios mais restritos para classificar o tipo de procedimento; a "
         "ampliada inclui casos ambíguos adicionais. A diferença entre as duas indica a sensibilidade "
         "dos resultados à regra de classificação.")

st.subheader("Limitações")
st.markdown(
    "1. Processo, vítima, ocorrência e registro da API são unidades distintas; contagens processuais "
    "não são número de vítimas ou agressões.\n"
    "2. Os dados públicos não representam todo o acervo: sigilo, preenchimento e classificação geram "
    "seleção e lacunas.\n"
    "3. A fonte judicial não elimina a subnotificação; acrescenta uma perspectiva com seus próprios "
    "filtros de acesso à Justiça.\n"
    "4. O município do órgão julgador não comprova o município do fato nem a residência da vítima.\n"
    "5. Município-sede não equivale a comarca nem ao conjunto de municípios atendidos.\n"
    "6. O órgão da capa é o órgão atual; eventos históricos não são atribuídos automaticamente a ele.\n"
    "7. Ajuizamento não equivale necessariamente a pedido de medida protetiva; atualização do índice "
    "não é evento judicial.\n"
    "8. Movimento genérico de decisão não comprova concessão, indeferimento ou encerramento; ausência "
    "de evento não comprova que ele não ocorreu.\n"
    "9. Análises descritivas não demonstram causas da violência, eficácia de políticas ou redução de "
    "crimes.\n"
    "10. Diferenças entre unidades não indicam eficiência sem considerar composição dos casos, "
    "cobertura e qualidade dos dados."
)

st.subheader("Nomes de medida na fonte")
st.write("Alguns nomes de medida protetiva chegam truncados e com codificação de caracteres quebrada "
         "na fonte. O painel corrige apenas o rótulo exibido; os dados publicados não são alterados.")

st.subheader("2019 como ano de sensibilidade")
st.write("A base de 2019 ultrapassa os casos novos de feminicídio do CNJ (115%) e tem 50,6% dos casos "
         "de violência doméstica, contra cerca de 20% nos demais anos. A tabela de 2019 do CNJ vem de "
         "outro produto, anterior ao painel, com critério possivelmente diferente. Por isso 2019 é "
         "tratado como ano de sensibilidade nas séries.")

st.subheader("Código-fonte")
st.markdown("Repositório: https://github.com/LuizCenci/TCC2")
