# Busca no SGT/CNJ os movimentos de medida protetiva e sua hierarquia. Uso: python sgt_movimentos_mp.py <dir_scripts> <saida.json>
import json, re, html, sys
sys.path.insert(0, sys.argv[1])
from sgt import call, parents, item
res = {}
for termo in ("Medida protetiva", "Protetiva"):
    t = call("pesquisarItemPublicoWS", f"<tipoTabela>M</tipoTabela><tipoPesquisa>N</tipoPesquisa><valorPesquisa>{termo}</valorPesquisa>")
    for c, n in re.findall(r"<cod_item[^>]*>(\d+)</cod_item>.*?<nome[^>]*>(.*?)</nome>", t, re.S):
        c = int(c)
        if c in res: continue
        ps = parents(c, "M")
        res[c] = {"nome": html.unescape(n).strip(), "pais": [{"codigo": p, "nome": item(p, "M")["nome"]} for p in ps if p != c]}
json.dump(res, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
for c, v in res.items(): print(c, v["nome"], "<-", " > ".join(f'{p["codigo"]} {p["nome"]}' for p in v["pais"]))
