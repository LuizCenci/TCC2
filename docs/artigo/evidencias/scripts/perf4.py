# Primeira página de 2019 (com track_total_hits), variando size, para achar margem sob o limite de 60 s do gateway.
import json, sys, time
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
import q
from datajud_tcc.catalog import Catalog
from datajud_tcc.config import CollectionConfig
from datajud_tcc.query import build_main_query
cfg = CollectionConfig.from_yaml(Path("config/collection.bronze.yaml"))
cat = Catalog.load(Path("config/catalogs/tjpr_vcm_2026-10-18.yaml"))
res = []
for size in (500, 250):
    b = build_main_query(cfg, cat, 2019); b["size"] = size
    t = time.time()
    r = q.requests.post(q.URL, json=b, headers={"Authorization": f"APIKey {q.KEY}", "Content-Type": "application/json"}, timeout=(10, 180))
    wall = round(time.time() - t, 1)
    d = r.json() if r.status_code == 200 else {}
    row = {"size": size, "status": r.status_code, "took_ms": d.get("took"), "wall_s": wall, "hits": len(d.get("hits", {}).get("hits", [])), "bytes": len(r.content), "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
    res.append(row); print(row, flush=True); time.sleep(5)
json.dump(res, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
