"""Carga do território IBGE (municípios e mesorregiões) no PostGIS."""

import json
from pathlib import Path

from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.referencias import ler_csv

ARQ_MALHA = "malha_municipios_pr.geojson"


def carregar_territorio(conn, dir=Path("config/gold")) -> dict:
    """Recarrega ref.municipio e ref.mesorregiao (TRUNCATE + carga); sem commit."""
    dir = Path(dir)
    aplicar_esquema_gold(conn)
    malha = json.loads((dir / ARQ_MALHA).read_text(encoding="utf-8"))
    geoms = {
        int(f["properties"]["codarea"]): json.dumps(f["geometry"])
        for f in malha["features"]
    }
    linhas = ler_csv("ref_municipio_pr.csv", dir)
    faltantes = {int(r["municipio_ibge"]) for r in linhas} - set(geoms)
    if faltantes:
        raise ValueError(f"municípios sem geometria na malha: {sorted(faltantes)[:5]}")

    conn.execute("TRUNCATE ref.municipio, ref.mesorregiao")
    with conn.cursor() as cur:
        for r in linhas:
            cod = int(r["municipio_ibge"])
            cur.execute(
                """INSERT INTO ref.municipio (municipio_ibge, municipio,
                       mesorregiao_id, mesorregiao, regiao_intermediaria_id,
                       regiao_intermediaria, pop_feminina_censo2022, geom)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,
                       ST_Multi(ST_MakeValid(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4674))))""",
                (
                    cod,
                    r["municipio"],
                    int(r["mesorregiao_id"]),
                    r["mesorregiao"],
                    int(r["regiao_intermediaria_id"]) if r["regiao_intermediaria_id"] else None,
                    r["regiao_intermediaria"] or None,
                    int(r["pop_feminina_censo2022"]) if r["pop_feminina_censo2022"] else None,
                    geoms[cod],
                ),
            )
    conn.execute(
        """INSERT INTO ref.mesorregiao (mesorregiao_id, mesorregiao, n_municipios,
               pop_feminina_censo2022, geom)
           SELECT mesorregiao_id, min(mesorregiao), count(*),
                  sum(pop_feminina_censo2022)::int,
                  ST_Multi(ST_CollectionExtract(ST_MakeValid(ST_Union(geom)), 3))
           FROM ref.municipio GROUP BY mesorregiao_id"""
    )
    n_mun = conn.execute("SELECT count(*) FROM ref.municipio").fetchone()[0]
    n_meso = conn.execute("SELECT count(*) FROM ref.mesorregiao").fetchone()[0]
    return {"municipios": n_mun, "mesorregioes": n_meso}
