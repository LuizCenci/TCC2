"""Supressão de células pequenas (primária e secundária) em linhas de agregados."""
from __future__ import annotations


def aplicar(linhas: list[dict], *, limite: int, colunas_grupo: tuple[str, ...],
            colunas_valor: tuple[str, ...]) -> list[dict]:
    saida = [dict(l) for l in linhas]
    for l in saida:
        l["suprimido"] = l["n"] < limite
    grupos: dict[tuple, list[dict]] = {}
    for l in saida:
        grupos.setdefault(tuple(l.get(c) for c in colunas_grupo), []).append(l)
    for membros in grupos.values():
        if sum(1 for l in membros if l["suprimido"]) == 1:
            restantes = [l for l in membros if not l["suprimido"]]
            if restantes:
                min(restantes, key=lambda l: l["n"])["suprimido"] = True
    for l in saida:
        if l["suprimido"]:
            l["n"] = None
            for c in colunas_valor:
                l[c] = None
    return saida
