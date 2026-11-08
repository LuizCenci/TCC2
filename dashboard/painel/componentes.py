"""Componentes compartilhados entre as páginas."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from painel import config, dados
from painel.exibicao import MSG_TUDO_SUPRIMIDO
from painel.rotulos import SERIE


@st.cache_data(show_spinner=False)
def _tabela_em_cache(nome: str, pasta: str) -> pd.DataFrame:
    return dados.carregar_tabela(nome, pasta=Path(pasta))


def tabela(nome: str) -> pd.DataFrame:
    """Lê um CSV da exportação; o cache é chaveado pela pasta vigente."""
    return _tabela_em_cache(nome, str(config.PASTA_EXPORTACAO)).copy()


def serie_selecionada() -> str:
    return st.session_state.get("serie", "estrita")


def rodape(definicao: str, arquivo: str, serie: str | None = None) -> None:
    partes = [definicao, "Unidade: processos públicos."]
    if serie:
        partes.append(f"Série: {SERIE.get(serie, serie).lower()}.")
    partes.append(f"Fonte: `{arquivo}`.")
    st.caption(" ".join(partes))


def botao_download(df: pd.DataFrame, nome: str) -> None:
    st.download_button(
        "Baixar CSV dos dados exibidos",
        data=df.to_csv(index=False).encode("utf-8-sig"),
        file_name=nome,
        mime="text/csv",
        key=f"download_{nome}",
    )


def grafico_ou_aviso(fig: go.Figure | None) -> None:
    if fig is None:
        st.info(MSG_TUDO_SUPRIMIDO)
    else:
        st.plotly_chart(fig, width="stretch")
