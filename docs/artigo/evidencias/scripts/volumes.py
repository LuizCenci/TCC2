# Volume por código e por grupo no recorte final (G1, 2019-2026), a partir do filtro do projeto.
import json, sys
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
from q import search
from datajud_tcc.catalog import Catalog
from datajud_tcc.config import CollectionConfig
from datajud_tcc.query import build_main_query, _thematic_filter
cfg = CollectionConfig.from_yaml(Path("config/collection.bronze.yaml"))
cat = Catalog.load(Path("config/catalogs/tjpr_vcm_2026-10-18.yaml"))
core = list(cat.subject_codes)
grp = lambda g, t: [e.codigo for e in cat.extensions if e.grupo == g and e.tipo == t]
def has(g):
    s = [{"terms": {"assuntos.codigo": grp(g, "assunto")}}] if grp(g, "assunto") else []
    if grp(g, "classe"): s.append({"terms": {"classe.codigo": grp(g, "classe")}})
    return {"bool": {"should": s, "minimum_should_match": 1}}
pvd = {"terms": {"assuntos.codigo": core}}
# Atribuição hierárquica exclusiva: núcleo > específica > ambígua > secundária.
excl = {
 "1_nucleo_pvd": {"bool": {"filter": [pvd]}},
 "2_especifica_sem_pvd": {"bool": {"filter": [has("especifica")], "must_not": [pvd]}},
 "3_ambigua_apenas": {"bool": {"filter": [has("ambigua")], "must_not": [pvd, has("especifica")]}},
 "4_secundaria_apenas": {"bool": {"filter": [has("secundaria")], "must_not": [pvd, has("especifica"), has("ambigua")]}},
}
body = {"size": 0, "track_total_hits": True,
 "query": {"bool": {"filter": [{"term": {"grau.keyword": "G1"}}, {"range": {"dataAjuizamento": {"gte": "20190101000000", "lt": "20270101000000"}}}, _thematic_filter(cat)]}},
 "aggs": {
  "assunto": {"terms": {"field": "assuntos.codigo", "include": core + list(cat.extension_subject_codes) + [12195, 12197, 15174, 15180], "size": 50}},
  "classe": {"terms": {"field": "classe.codigo", "include": list(cat.extension_class_codes), "size": 10}},
  "ano": {"filters": {"filters": {str(y): {"range": {"dataAjuizamento": {"gte": f"{y}0101000000", "lt": f"{y+1}0101000000"}}} for y in cfg.years}},
          "aggs": {"grupo": {"filters": {"filters": excl}}}}}}
st, d = search(body)
json.dump({"status": st, "body": body, "response": d}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False)
a = d["aggregations"]; print(st, d["hits"]["total"])
print({b["key"]: b["doc_count"] for b in a["assunto"]["buckets"]}); print({b["key"]: b["doc_count"] for b in a["classe"]["buckets"]})
for y, v in a["ano"]["buckets"].items(): print(y, v["doc_count"], {k: w["doc_count"] for k, w in v["grupo"]["buckets"].items()})
