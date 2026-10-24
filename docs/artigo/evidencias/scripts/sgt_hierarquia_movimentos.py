# Hierarquia SGT/CNJ dos códigos de movimento mais frequentes da Bronze.
# Uso: python sgt_hierarquia_movimentos.py <dir_scripts> <nomes_movimentos.json> <N> <saida.json>
import json, sys
sys.path.insert(0, sys.argv[1])
from sgt import parents, item
mov = json.load(open(sys.argv[2], encoding="utf-8"))["movimentos"]
top = [int(c) for c in list(mov)[: int(sys.argv[3])] if c not in ("None", "-1")]
nome_cache, res = {}, {}
def nome(c):
    if c not in nome_cache: nome_cache[c] = item(c, "M")["nome"]
    return nome_cache[c]
for c in top:
    ps = [p for p in parents(c, "M") if p != c]
    res[str(c)] = {"nome_api": mov[str(c)]["nome"], "nome_sgt": nome(c), "ocorrencias": mov[str(c)]["ocorrencias"],
                   "caminho": [{"codigo": p, "nome": nome(p)} for p in ps]}
    print(c, res[str(c)]["nome_sgt"], "<-", " > ".join(x["nome"] or "?" for x in res[str(c)]["caminho"]), flush=True)
json.dump(res, open(sys.argv[4], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
