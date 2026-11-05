# Distribuição de dataHoraUltimaAtualizacao e @timestamp no recorte temático G1 (size=0, só agregações).
import json, sys, time
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
from q import search
from datajud_tcc.catalog import Catalog
from datajud_tcc.query import _thematic_filter
cat = Catalog.load(Path("config/catalogs/tjpr_vcm_2026-10-18.yaml"))
body = {"size": 0, "track_total_hits": True, "query": {"bool": {"filter": [{"term": {"grau.keyword": "G1"}}, _thematic_filter(cat),
        {"range": {"dataAjuizamento": {"gte": "20190101000000", "lt": "20270101000000"}}}]}},
        "aggs": {f: {"date_histogram": {"field": f, "calendar_interval": "month", "min_doc_count": 1}} for f in ("dataHoraUltimaAtualizacao", "@timestamp")}
                | {"dia_ultima": {"date_histogram": {"field": "dataHoraUltimaAtualizacao", "calendar_interval": "day", "min_doc_count": 500}}}}
st, d = search(body)
json.dump({"consultado_em": time.strftime("%Y-%m-%dT%H:%M:%S"), "status": st, "total": d.get("hits", {}).get("total"), "aggs": d.get("aggregations")},
          open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(st, d.get("hits", {}).get("total"))
for f in ("dataHoraUltimaAtualizacao", "@timestamp", "dia_ultima"):
    print("==", f); [print(" ", b["key_as_string"][:10], b["doc_count"]) for b in d["aggregations"][f]["buckets"][-14:]]
