"""Formatação brasileira e textos de exibição."""
from __future__ import annotations

import pandas as pd

MSG_TUDO_SUPRIMIDO = "Todos os valores deste recorte foram suprimidos para proteger a privacidade."


def _ausente(v) -> bool:
    return v is None or bool(pd.isna(v))


def _br(texto: str) -> str:
    return texto.replace(",", "\0").replace(".", ",").replace("\0", ".")


def formatar_inteiro(v) -> str:
    if _ausente(v):
        return "—"
    return f"{int(round(float(v))):,}".replace(",", ".")


def formatar_decimal(v, casas: int = 1) -> str:
    if _ausente(v):
        return "—"
    return _br(f"{float(v):,.{casas}f}")


def formatar_pct(v, casas: int = 1) -> str:
    if _ausente(v):
        return "—"
    return formatar_decimal(v, casas) + "%"


def valor_ou_suprimido(v, suprimido: bool, formatador=formatar_inteiro) -> str:
    if suprimido:
        return "suprimido"
    return formatador(v)


def texto_mediana(linha: pd.Series) -> str:
    if not linha["estimavel"]:
        return "não estimável"
    if not linha["mediana_alcancada"]:
        return "mediana não alcançada"
    dias = "dia" if int(round(float(linha["mediana_dias"]))) == 1 else "dias"
    return (f"{formatar_inteiro(linha['mediana_dias'])} {dias} "
            f"(IC 95%: {formatar_inteiro(linha['ic95_inf'])}–{formatar_inteiro(linha['ic95_sup'])})")


def rotulo_ano(ano: int, parcial: bool) -> str:
    return f"{ano} (parcial)" if parcial else str(ano)


def colunas_tempo(linhas: pd.DataFrame) -> pd.DataFrame:
    """Colunas numéricas de tempo (mediana, IC, situação, n); suprimido vira vazio com motivo."""
    sup = linhas["suprimido"].astype(bool).tolist()
    med, ic, sit, n = [], [], [], []
    for x, (_, r) in zip(sup, linhas.iterrows()):
        if x:
            med.append(float("nan")); ic.append(""); sit.append("suprimido"); n.append(float("nan"))
            continue
        n.append(float(r["n"]) if not _ausente(r["n"]) else float("nan"))
        if not r["estimavel"]:
            med.append(float("nan")); ic.append(""); sit.append("não estimável")
        elif not r["mediana_alcancada"]:
            med.append(float("nan")); ic.append(""); sit.append("mediana não alcançada")
        else:
            med.append(float(r["mediana_dias"]))
            ic.append(f"{formatar_inteiro(r['ic95_inf'])}–{formatar_inteiro(r['ic95_sup'])}")
            sit.append("")
    return pd.DataFrame({"Mediana (dias)": med, "IC 95% (dias)": ic, "Situação": sit,
                         "Processos (n, arredondado)": n}, index=linhas.index)
