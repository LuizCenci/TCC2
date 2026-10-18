# Mede o tempo do servidor (took) para variações da consulta de paginação.
import json, sys, time, copy
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
from q import search
base = json.load(open(sys.argv[2], encoding="utf-8"))  # request de uma página com search_after
res = []
for label, mod in (("igual", {}), ("sem_track_total", {"track_total_hits": False}), ("size1000_sem_track", {"track_total_hits": False, "size": 1000})):
    b = copy.deepcopy(base); b.update(mod)
    t = time.time(); st, d = search(b)
    r = {"variante": label, "status": st, "took_ms": d.get("took"), "wall_s": round(time.time()-t, 1), "hits": len(d.get("hits", {}).get("hits", [])), "mod": mod, "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
    res.append(r); print(r, flush=True); time.sleep(3)
json.dump(res, open(sys.argv[3], "w", encoding="utf-8"), indent=1)
