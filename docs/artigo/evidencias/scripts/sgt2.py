import sys, json
from sgt import parents, item
res={}
for c in [15174,15180,7792,7793,14238,14958,10606]:
    ps=parents(c,"A"); res[c]={"nome":item(c,"A")["nome"],"pais":[(p,item(p,"A")["nome"]) for p in ps if p!=c]}
json.dump(res,open(sys.argv[1],"w",encoding="utf-8"),ensure_ascii=False,indent=1)
