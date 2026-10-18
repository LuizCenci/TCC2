import json, sys
from sgt import parents, item
res = json.load(open(sys.argv[1], encoding="utf-8"))
for c, tab in ((12358,"A"),(15511,"A"),(12197,"A"),(15174,"A"),(15180,"A"),(15309,"C"),(12423,"C")):
    ps = parents(c, tab)
    res[f"{tab}{c}"] = {"codigo": c, "tabela": tab, **item(c, tab), "pais": [{"codigo": p, "nome": item(p, tab)["nome"]} for p in ps if p != c]}
    print(tab, c, res[f"{tab}{c}"]["nome"], [p["nome"] for p in res[f"{tab}{c}"]["pais"]])
json.dump(res, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
