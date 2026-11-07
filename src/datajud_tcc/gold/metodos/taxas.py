"""Taxas por 100 mil mulheres com Bayes empírico global (Marshall).

Fórmula (taxas por pessoa; o fator 100.000 só entra na gravação):
  r_i = n_i / P_i;  m = Σn / ΣP;  s² = Σ P_i (r_i - m)² / ΣP - m / P̄  (P̄ = média de P_i);
  s² < 0 vira 0;  C_i = s² / (s² + m / P_i);  taxa_eb_i = m + C_i (r_i - m).
Mesorregiões com P_i ausente ou 0 saem de m, s² e P̄ e recebem None.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FATOR = 100_000


def bayes_empirico_global(casos: list[int], populacao: list[int]) -> list[float | None]:
    n = np.array([float(c) for c in casos])
    p = np.array([float(x) if x else 0.0 for x in populacao])
    ok = p > 0
    out: list[float | None] = [None] * len(n)
    if not ok.any():
        return out
    no, po = n[ok], p[ok]
    r = no / po
    m = no.sum() / po.sum()
    s2 = max((po * (r - m) ** 2).sum() / po.sum() - m / po.mean(), 0.0)
    denom = s2 + m / po
    c = np.where(denom > 0, s2 / np.where(denom > 0, denom, 1.0), 0.0)
    eb = m + c * (r - m)
    for i, v in zip(np.flatnonzero(ok), eb):
        out[int(i)] = float(v)
    return out


def construir_agg_taxa(conn) -> int:
    meso = pd.DataFrame(
        conn.execute("SELECT mesorregiao_id, pop_feminina_censo2022 FROM ref.mesorregiao"
                     " ORDER BY mesorregiao_id").fetchall(),
        columns=["meso", "pop"])
    vol = pd.DataFrame(
        conn.execute("SELECT ano, ano_parcial, tipo, serie, meso, sum(n) FROM gold.agg_volume"
                     " WHERE meso IS NOT NULL GROUP BY 1, 2, 3, 4, 5").fetchall(),
        columns=["ano", "parcial", "tipo", "serie", "meso", "n"])
    conn.execute("TRUNCATE gold.agg_taxa")
    linhas = []
    if not vol.empty:
        chaves = vol[["ano", "parcial", "tipo", "serie"]].drop_duplicates()
        for ch in chaves.itertuples(index=False):
            sub = vol[(vol.ano == ch.ano) & (vol.tipo == ch.tipo) & (vol.serie == ch.serie)]
            nmap = dict(zip(sub.meso, sub.n))
            casos = [int(nmap.get(m, 0)) for m in meso["meso"]]
            pops = [int(p) if p == p and p is not None else 0 for p in meso["pop"]]
            eb = bayes_empirico_global(casos, pops)
            for m, n, p, e in zip(meso["meso"], casos, pops, eb):
                linhas.append(("Q02", int(ch.ano), bool(ch.parcial), ch.tipo, ch.serie, int(m),
                               n, p or None, n / p * FATOR if p else None,
                               e * FATOR if e is not None else None))
    if linhas:
        with conn.cursor() as cur:
            cur.executemany(
                "INSERT INTO gold.agg_taxa (pergunta, ano_ajuizamento, ano_parcial,"
                " tipo_procedimento, serie, mesorregiao_id, n, pop_feminina, taxa_bruta_100k,"
                " taxa_eb_100k) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", linhas)
    return len(linhas)
