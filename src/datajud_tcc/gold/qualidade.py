"""Resumo de qualidade da Gold (lê as views e gold.fato_processo)."""


def resumo(conn) -> dict:
    r = conn.execute(
        """SELECT count(*),
                  count(*) FILTER (WHERE mesorregiao_id IS NULL),
                  count(*) FILTER (WHERE evento_antes_ajuizamento),
                  count(*) FILTER (WHERE numero_repetido),
                  count(*) FILTER (WHERE removido_indice)
             FROM gold.fato_processo""").fetchone()
    c = conn.execute(
        "SELECT tipo_outros_pct, sem_categoria_pct FROM gold.qualidade_cobertura_referencias"
    ).fetchone()
    dup = conn.execute(
        "SELECT COALESCE(sum(n_processos), 0) FROM gold.qualidade_movimentos_duplicados"
    ).fetchone()[0]
    return {
        "registros": r[0], "sem_mesorregiao": r[1],
        "tipo_outros_pct": float(c[0] or 0), "sem_categoria_pct": float(c[1] or 0),
        "eventos_antes_ajuizamento": r[2], "numero_repetido": r[3],
        "removido_indice": r[4], "movimentos_duplicados_processos": int(dup),
    }
