# Isola o custo: ordenação vs. busca do _source.
import json, sys, time, copy
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
from q import search
base = json.load(open(sys.argv[2], encoding="utf-8"))
res = []
for label, mod, drop in (
    ("sort_id_sem_source", {"_source": False, "track_total_hits": False}, []),
    ("sem_sort_com_source", {"track_total_hits": False}, ["sort", "search_after"]),
    ("sort_doc_com_source", {"track_total_hits": False, "sort": ["_doc"]}, ["search_after"]),
):
    b = copy.deepcopy(base); b.update(mod)
    for k in drop: b.pop(k, None)
    t = time.time(); st, d = search(b)
    r = {"variante": label, "status": st, "took_ms": d.get("took"), "wall_s": round(time.time()-t, 1), "hits": len(d.get("hits", {}).get("hits", [])), "quando": time.strftime("%Y-%m-%dT%H:%M:%S")}
    res.append(r); print(r, flush=True); time.sleep(3)
json.dump(res, open(sys.argv[3], "w", encoding="utf-8"), indent=1)
