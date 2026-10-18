# Monta mapa código->nome de assuntos e classes a partir de amostras (_source restrito).
import json, sys, time
sys.path.insert(0, sys.argv[1]); from q import search
PVD=[10948,10949,11979,12194,12196,14097,14098,14226,14227,14228,14229,14942,14943,14944,14945]
agg = json.load(open(sys.argv[2], encoding="utf-8"))["response"]["aggregations"]
want_a = {b["key"] for b in agg["assunto"]["buckets"]}; want_c = {b["key"] for b in agg["classe"]["buckets"]}
A, C = {}, {}
def walk(x):
    if isinstance(x, dict):
        if "codigo" in x and "nome" in x: yield x
        for v in x.values(): yield from walk(v)
    elif isinstance(x, list):
        for v in x: yield from walk(v)
def absorb(hits):
    for h in hits:
        s=h["_source"]
        for a in walk(s.get("assuntos", [])): A.setdefault(a["codigo"], a["nome"])
        c=s.get("classe") or {}
        if "codigo" in c: C.setdefault(c["codigo"], c["nome"])
for it in range(12):
    ma = sorted(want_a - set(A)); mc = sorted(want_c - set(C))
    print("faltam", len(ma), len(mc), flush=True)
    if not ma and not mc: break
    should = []
    if ma: should.append({"terms":{"assuntos.codigo":ma}})
    if mc: should.append({"terms":{"classe.codigo":mc}})
    body={"size":1000,"_source":["assuntos","classe"],"query":{"bool":{"filter":[{"terms":{"assuntos.codigo":PVD}}],"should":should,"minimum_should_match":1}}}
    st, d = search(body)
    if st!=200: print(st, str(d)[:300]); break
    absorb(d["hits"]["hits"]); time.sleep(2)
json.dump({"assuntos":{str(k):v for k,v in A.items()},"classes":{str(k):v for k,v in C.items()}}, open(sys.argv[3],"w",encoding="utf-8"), ensure_ascii=False, indent=0)
print("ok", len(A), len(C), "sem nome:", sorted(want_a-set(A))[:40], sorted(want_c-set(C)))
