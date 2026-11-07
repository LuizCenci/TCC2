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


def _horizonte_valido(duracoes, h: int) -> bool:
    """Horizonte só com seguimento (h <= maior duração) e pelo menos N_MIN em risco (duração >= h)."""
    return bool(len(duracoes)) and h <= max(duracoes) and sum(1 for d in duracoes if d >= h) >= N_MIN


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
        if not _horizonte_valido(duracoes, h):
            continue
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


# ---------------------------------------------------------------- Q10: riscos competitivos
HORIZONTES_IA = (365, 730, 1095, 1825)
CAUSAS = {1: "CONDENACAO", 2: "ABSOLVICAO", 3: "EXTINCAO_PUNIBILIDADE", 4: "PRESCRICAO",
          5: "OUTRO_ENCERRAMENTO"}
DESFECHO_PARA_CAUSA = {
    "CONDENACAO": 1, "ABSOLVICAO": 2, "EXTINCAO_PUNIBILIDADE": 3, "PRESCRICAO": 4,
    "SEM_MERITO": 5, "REJEICAO_DENUNCIA": 5, "ARQUIVAMENTO_INVESTIGACAO": 5,
    "ENCERRADO_SEM_DESFECHO": 5, "EM_ANDAMENTO": 0,
}
COORTES = (("2019-2021", 2019, 2021), ("2022-2023", 2022, 2023), ("2024-2026", 2024, 2026))


def incidencia_acumulada(duracoes: list[int], causas: list[int],
                         horizontes: tuple[int, ...] = HORIZONTES_IA) -> dict[int, dict[int, float]]:
    """Causa -> {horizonte -> incidência acumulada (%)}; causa 0 = censura.

    Aalen-Johansen exato em tempo discreto (sem jitter): em cada duração distinta t,
    n(t) = em risco (duração >= t), d(t) = eventos de qualquer causa, d_k(t) = eventos da causa k;
    censuras em t saem do risco depois dos eventos de t. S(t) = prod(1 - d/n),
    CIF_k(t) = soma de S(u-) * d_k(u)/n(u). O valor no horizonte h é o do maior t <= h.
    n < 30 devolve {}; horizonte maior que a maior duração observada devolve None;
    causa sem eventos em estrato estimável devolve 0.0.
    """
    import numpy as np

    if len(duracoes) < N_MIN:
        return {}
    dur = np.asarray(duracoes, dtype=float)
    cau = np.asarray(causas, dtype=int)
    ts = np.unique(dur)
    n_risco = np.array([(dur >= t).sum() for t in ts], dtype=float)
    d_tot = np.array([((dur == t) & (cau != 0)).sum() for t in ts], dtype=float)
    surv = np.cumprod(1 - d_tot / n_risco)
    surv_antes = np.concatenate(([1.0], surv[:-1]))
    maxd = ts[-1]
    out: dict[int, dict[int, float]] = {}
    for k in sorted({int(c) for c in cau if c != 0}):
        d_k = np.array([((dur == t) & (cau == k)).sum() for t in ts], dtype=float)
        cif = np.cumsum(surv_antes * d_k / n_risco)
        res = {}
        for h in horizontes:
            if h > maxd or not _horizonte_valido(duracoes, h):
                res[h] = None
                continue
            idx = np.searchsorted(ts, h, side="right") - 1
            res[h] = float(cif[idx] * 100) if idx >= 0 else 0.0
        out[k] = res
    return out


def _linhas_desfecho(tipo, serie, variante, estrato, valor, g):
    dur = [int(x) for x in g.duracao_dias]
    causas = [int(x) for x in g.causa]
    n = len(dur)
    ia = incidencia_acumulada(dur, causas) if n >= N_MIN else {}
    linhas = []
    for k, nome in CAUSAS.items():
        nd = sum(1 for c in causas if c == k)
        r = ia.get(k) or {}
        if n >= N_MIN and not r:
            r = {h: 0.0 if _horizonte_valido(dur, h) else None for h in HORIZONTES_IA}
        linhas.append(("Q10", tipo, serie, variante, estrato, str(valor), nome, n, nd, n >= N_MIN,
                       *[r.get(h) for h in HORIZONTES_IA]))
    return linhas


def construir_agg_desfecho(conn) -> int:
    cols = ["tipo_procedimento", "serie_estrita", "ano_ajuizamento", "mesorregiao_id",
            "desfecho", "duracao_dias", "reativado"]
    df = pd.DataFrame(
        conn.execute(f"SELECT {', '.join(cols)} FROM gold.fato_processo"
                     " WHERE tipo_procedimento IN ('ACAO_PENAL','INQUERITO')"
                     " AND duracao_dias IS NOT NULL AND duracao_dias >= 0").fetchall(), columns=cols)
    df["causa"] = df["desfecho"].map(DESFECHO_PARA_CAUSA)
    df = df[df.causa.notna()].copy()
    df["causa"] = df["causa"].astype(int)
    df["reativado"] = df["reativado"].fillna(False).astype(bool)
    linhas = []
    for tipo in ("ACAO_PENAL", "INQUERITO"):
        t = df[df.tipo_procedimento == tipo]
        for serie in ("estrita", "ampliada"):
            s = t[t.serie_estrita.astype(bool)] if serie == "estrita" else t
            for variante in ("principal", "com_reativados"):
                v = s[~s.reativado] if variante == "principal" else s
                if v.empty:
                    continue
                linhas += _linhas_desfecho(tipo, serie, variante, "total", "total", v)
                for nome, a, b in COORTES:
                    c = v[(v.ano_ajuizamento >= a) & (v.ano_ajuizamento <= b)]
                    if not c.empty:
                        linhas += _linhas_desfecho(tipo, serie, variante, "coorte", nome, c)
                c = v[(v.ano_ajuizamento >= 2019) & (v.ano_ajuizamento <= 2021)]
                for valor, g in c.groupby("mesorregiao_id", dropna=True):
                    linhas += _linhas_desfecho(tipo, serie, variante, "mesorregiao_id",
                                               int(valor), g)
    conn.execute("TRUNCATE gold.agg_desfecho")
    if linhas:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO gold.agg_desfecho (pergunta, tipo_procedimento, serie, variante,"
                " estrato, valor_estrato, desfecho, n, n_desfecho, estimavel, ia_365, ia_730,"
                " ia_1095, ia_1825) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", linhas)
    return len(linhas)
