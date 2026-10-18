# Valida o filtro do código (build_main_query) contra a API: size=0, contagem exata por ano.
import json, sys, time
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
from q import search
from datajud_tcc.catalog import Catalog
from datajud_tcc.config import CollectionConfig
from datajud_tcc.query import build_main_query
cfg = CollectionConfig.from_yaml(Path("config/collection.bronze.yaml"))
cat = Catalog.load(Path("config/catalogs/tjpr_vcm_2026-10-18.yaml"))
out = {"catalog_version": cat.version, "catalog_sha256": cat.source_hash, "years": {}}
for y in cfg.years:
    body = build_main_query(cfg, cat, y); body["size"] = 0
    st, d = search(body)
    out["years"][y] = {"status": st, "total": d["hits"]["total"], "timed_out": d.get("timed_out"), "shards_failed": d.get("_shards", {}).get("failed")}
    print(y, out["years"][y], flush=True); time.sleep(2)
out["sum"] = sum(v["total"]["value"] for v in out["years"].values())
out["query_example_2019"] = build_main_query(cfg, cat, 2019)
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("soma", out["sum"])
