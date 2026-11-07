"""Supressão de células pequenas (primária, secundária e de subcontagens)."""
from __future__ import annotations


def aplicar(linhas: list[dict], *, limite: int, colunas_grupo: tuple[str, ...],
            colunas_valor: tuple[str, ...], colunas_contagem: tuple[str, ...] = ()) -> list[dict]:
    """Cópias com `suprimido` e `suprimido_parcial`. `colunas_contagem` (subcontagens < limite)
    são zeradas para None mesmo com n >= limite; estimativas só caem se n for suprimido."""
    saida = [dict(l) for l in linhas]
    for l in saida:
        l["suprimido"] = l["n"] is None or l["n"] < limite
    grupos: dict[tuple, list[dict]] = {}
    for l in saida:
        grupos.setdefault(tuple(l.get(c) for c in colunas_grupo), []).append(l)
    for membros in grupos.values():
        if sum(1 for l in membros if l["suprimido"]) == 1:
            restantes = [l for l in membros if not l["suprimido"]]
            if restantes:
                min(restantes, key=lambda l: l["n"])["suprimido"] = True
    for l in saida:
        l["suprimido_parcial"] = False
        if l["suprimido"]:
            l["n"] = None
            for c in colunas_valor:
                l[c] = None
        else:
            for c in colunas_contagem:
                if l.get(c) is not None and l[c] < limite:
                    l[c] = None
                    l["suprimido_parcial"] = True
    return saida
