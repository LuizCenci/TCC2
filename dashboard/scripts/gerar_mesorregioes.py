"""Gera dashboard/dados/mesorregioes_pr.geojson (10 mesorregiões do Paraná).

Fonte: malha municipal do IBGE já usada na Gold (config/gold/malha_municipios_pr.geojson)
e a referência config/gold/ref_municipio_pr.csv (município -> mesorregião).
Os municípios são dissolvidos por mesorregião e simplificados (0,005 grau).
Uso, da raiz do repositório (requer shapely, só no .venv):
    .venv/Scripts/python.exe dashboard/scripts/gerar_mesorregioes.py
"""
import csv
import json
from pathlib import Path

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

RAIZ_REPO = Path(__file__).resolve().parents[2]
MALHA = RAIZ_REPO / "config" / "gold" / "malha_municipios_pr.geojson"
REF = RAIZ_REPO / "config" / "gold" / "ref_municipio_pr.csv"
SAIDA = RAIZ_REPO / "dashboard" / "dados" / "mesorregioes_pr.geojson"
TOLERANCIA = 0.005


def _arredonda(c):
    if isinstance(c, (list, tuple)):
        return [_arredonda(x) for x in c]
    return round(c, 4)


def main() -> None:
    with open(REF, encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    por_mun = {r["municipio_ibge"]: (int(r["mesorregiao_id"]), r["mesorregiao"]) for r in linhas}
    nomes = {i: n for i, n in por_mun.values()}
    malha = json.loads(MALHA.read_text(encoding="utf-8"))
    grupos: dict[int, list] = {}
    for feat in malha["features"]:
        cod = str(feat["properties"]["codarea"])
        if cod in por_mun:
            grupos.setdefault(por_mun[cod][0], []).append(shape(feat["geometry"]))
    feats = []
    for mid in sorted(grupos):
        geom = unary_union(grupos[mid]).simplify(TOLERANCIA, preserve_topology=True)
        g = mapping(geom)
        feats.append({
            "type": "Feature",
            "properties": {"mesorregiao_id": mid, "mesorregiao": nomes[mid]},
            "geometry": {"type": g["type"], "coordinates": _arredonda(g["coordinates"])},
        })
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    for f in feats:
        print(f["properties"]["mesorregiao_id"], f["properties"]["mesorregiao"])
    print(f"{len(feats)} mesorregiões, {SAIDA.stat().st_size} bytes")


if __name__ == "__main__":
    main()
