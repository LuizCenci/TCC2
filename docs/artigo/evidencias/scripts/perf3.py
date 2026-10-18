# Isola o custo de cada filtro (size=100, sem track_total).
import json, sys, time, copy
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
from q import search
base = json.load(open(sys.argv[2], encoding="utf-8"))
f = base["query"]["bool"]["filter"]  # [range, grau, temático]
res = []
for label, filters in (("sem_range", [f[1], f[2]]), ("so_range_e_grau", [f[0], f[1]]), ("sem_tematico_sem_range", [f[1]])):
    b = copy.deepcopy(base); b["query"]["bool"]["filter"] = filters; b["track_total_hits"] = False
    t = time.time(); st, d = search(b)
    r = {"variante": label, "status": st, "took_ms": d.get("took"), "wall_s": round(time.time()-t, 1), "hits": len(d.get("hits", {}).get("hits", [])), "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
    res.append(r); print(r, flush=True); time.sleep(3)
json.dump(res, open(sys.argv[3], "w", encoding="utf-8"), indent=1)
