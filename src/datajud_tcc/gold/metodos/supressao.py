"""Supressão de células pequenas (primária, secundária, de subcontagens e dependentes)."""
from __future__ import annotations


def aplicar(linhas: list[dict], *, limite: int, colunas_grupo: tuple[str, ...],
            colunas_valor: tuple[str, ...], colunas_contagem: tuple[str, ...] = (),
            dependentes: dict[str, tuple[str, ...]] | None = None,
            conjuntos_aditivos: tuple[tuple[str, ...], ...] = ()) -> list[dict]:
    """Cópias com `suprimido` e `suprimido_parcial`. `colunas_contagem` (subcontagens < limite)
    são zeradas para None mesmo com n >= limite. `dependentes` mapeia coluna de contagem ->
    estimativas que também caem quando a contagem é anulada (primária ou subcontagem).
    `conjuntos_aditivos`: se exatamente uma coluna do conjunto é anulada, anula-se também a menor
    das restantes (impede recuperar a anulada por subtração do total)."""
    dependentes = dependentes or {}
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

    def anular(l, c):
        l[c] = None
        for d in dependentes.get(c, ()):
            l[d] = None

    for l in saida:
        l["suprimido_parcial"] = False
        if l["suprimido"]:
            l["n"] = None
            for c in colunas_valor:
                l[c] = None
            for c in dependentes:
                if c in l:
                    anular(l, c)
        else:
            for c in colunas_contagem:
                if l.get(c) is not None and l[c] < limite:
                    anular(l, c)
                    l["suprimido_parcial"] = True
            for conj in conjuntos_aditivos:
                presentes = [c for c in conj if c in l]
                nulas = [c for c in presentes if l[c] is None]
                if len(nulas) == 1:
                    outras = [c for c in presentes if l[c] is not None]
                    if outras:
                        anular(l, min(outras, key=lambda c: l[c]))
                        l["suprimido_parcial"] = True
    return saida
