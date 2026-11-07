"""Tempos até marcos processuais por Kaplan-Meier, com censura na data de corte."""
from __future__ import annotations

import math

import pandas as pd

N_MIN = 30
HORIZONTES = (2, 30, 365, 730)

# (pergunta, marco, tipo_procedimento, coluna do evento, exige deferimento)
DEFINICOES = [
    ("Q05", "decisao_mpu", "MPU", "dt_decisao_mpu", False),
    ("Q07", "revogacao_mpu", "MPU", "dt_revogacao_mpu", True),
    ("Q08", "recebimento_denuncia", "ACAO_PENAL", "dt_recebimento_denuncia", False),
    ("Q08", "recebimento_denuncia", "INQUERITO", "dt_recebimento_denuncia", False),
    ("Q09", "sentenca", "ACAO_PENAL", "dt_sentenca", False),
]
ESTRATOS = ("ano_ajuizamento", "mesorregiao_id", "orgao_especializado")


def _num(v):
    if v is None:
        return None
    v = float(v)
    return v if math.isfinite(v) else None


def estimar_km(duracoes: list[int], eventos: list[bool],
               horizontes: tuple[int, ...] = HORIZONTES) -> dict:
    n, ne = len(duracoes), int(sum(bool(e) for e in eventos))
    out = {"n": n, "n_eventos": ne, "estimavel": n >= N_MIN, "mediana_dias": None,
           "mediana_alcancada": None, "ic95_inf": None, "ic95_sup": None}
    for h in horizontes:
        out[f"pct_evento_ate_{h}"] = None
    if n < N_MIN:
        return out
    from lifelines import KaplanMeierFitter
    from lifelines.utils import median_survival_times

    kmf = KaplanMeierFitter().fit(duracoes, event_observed=[bool(e) for e in eventos])
    med = _num(kmf.median_survival_time_)
    out["mediana_alcancada"] = med is not None
    out["mediana_dias"] = med
    if med is not None:
        ci = median_survival_times(kmf.confidence_interval_)
        out["ic95_inf"] = _num(ci.iloc[0, 0])
        out["ic95_sup"] = _num(ci.iloc[0, 1])
    for h in horizontes:
        out[f"pct_evento_ate_{h}"] = float((1 - kmf.survival_function_at_times(h).iloc[0]) * 100)
    return out


def _linha(pergunta, marco, tipo, serie, estrato, valor, dur, ev):
    r = estimar_km(list(dur), list(ev))
    return (pergunta, marco, tipo, serie, estrato, str(valor), r["n"], r["n_eventos"], r["estimavel"],
            r["mediana_dias"], r["mediana_alcancada"], r["ic95_inf"], r["ic95_sup"],
            r["pct_evento_ate_2"], r["pct_evento_ate_30"], r["pct_evento_ate_365"],
            r["pct_evento_ate_730"])


def construir_agg_tempo(conn) -> int:
    cols = ["tipo_procedimento", "serie_estrita", "ano_ajuizamento", "mesorregiao_id",
            "orgao_especializado", "data_ajuizamento", "data_corte", "resultado_mpu",
            "dt_decisao_mpu", "dt_revogacao_mpu", "dt_recebimento_denuncia", "dt_sentenca"]
    df = pd.DataFrame(
        conn.execute(f"SELECT {', '.join(cols)} FROM gold.fato_processo"
                     " WHERE data_ajuizamento IS NOT NULL").fetchall(), columns=cols)
    df["aj"] = pd.to_datetime(df["data_ajuizamento"]).dt.normalize()
    corte = pd.to_datetime(df["data_corte"])
    linhas = []
    for pergunta, marco, tipo, col, defer in DEFINICOES:
        sub = df[df.tipo_procedimento == tipo]
        if defer:
            sub = sub[sub.resultado_mpu.isin(["DEFERIMENTO", "PARCIAL"])]
        evento = pd.to_datetime(sub[col])
        dur = (evento.fillna(corte[sub.index]) - sub["aj"]).dt.days
        sub = sub.assign(dur=dur, ev=evento.notna())
        sub = sub[sub.dur >= 0]
        for serie in ("estrita", "ampliada"):
            s = sub[sub.serie_estrita.astype(bool)] if serie == "estrita" else sub
            if s.empty:
                continue
            linhas.append(_linha(pergunta, marco, tipo, serie, "total", "total", s.dur, s.ev))
            for est in ESTRATOS:
                for valor, g in s.groupby(est, dropna=True):
                    v = bool(valor) if est == "orgao_especializado" else int(valor)
                    linhas.append(_linha(pergunta, marco, tipo, serie, est, v, g.dur, g.ev))
    conn.execute("TRUNCATE gold.agg_tempo")
    if linhas:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO gold.agg_tempo (pergunta, marco, tipo_procedimento, serie, estrato,"
                " valor_estrato, n, n_eventos, estimavel, mediana_dias, mediana_alcancada, ic95_inf,"
                " ic95_sup, pct_evento_ate_2, pct_evento_ate_30, pct_evento_ate_365,"
                " pct_evento_ate_730) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                linhas)
    return len(linhas)
