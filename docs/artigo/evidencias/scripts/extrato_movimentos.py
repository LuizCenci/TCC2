# Extrato compacto da Bronze (2019-2025) para análises de movimentos. Sem numeroProcesso nem id.
# Saída: JSON Lines gzip com classe, assuntos, órgão, município-sede, datas relativas e movimentos (código, dias).
# Uso: python -I extrato_movimentos.py <run_root> <saida.jsonl.gz> <nomes_movimentos.json>
import gzip, json, sys
from collections import Counter
from datetime import datetime
from pathlib import Path
root, out_path, names_path = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
COLETA = datetime(2026, 10, 18)
def dt(s):
    s = str(s)
    if len(s) == 14 and s.isdigit(): return datetime.strptime(s, "%Y%m%d%H%M%S")
    try: return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError: return None
def flat(x):
    if isinstance(x, dict): yield x
    elif isinstance(x, list):
        for v in x: yield from flat(v)
names = {}; counts = Counter(); n = 0
with gzip.open(out_path, "wt", encoding="utf-8") as out:
    for f in sorted(root.glob("responses/year=*/*.gz")):
        if f.parent.name == "year=2026": continue
        for h in json.loads(gzip.decompress(f.read_bytes()))["hits"]["hits"]:
            r = h["_source"]; d0 = dt(r.get("dataAjuizamento")); o = r.get("orgaoJulgador") or {}
            movs = []
            for m in r.get("movimentos") or []:
                c = m.get("codigo"); t = dt(m.get("dataHora")); counts[c] += 1; names.setdefault(c, m.get("nome"))
                movs.append([c, (t - d0).days if (t and d0) else None])
            movs.sort(key=lambda x: (x[1] is None, x[1]))
            out.write(json.dumps({"ano": d0.year, "mes": d0.month, "classe": (r.get("classe") or {}).get("codigo"),
                "assuntos": sorted({a.get("codigo") for a in flat(r.get("assuntos")) if a.get("codigo") is not None}),
                "orgao": o.get("nome"), "orgao_codigo": o.get("codigo"), "mun": o.get("codigoMunicipioIBGE"),
                "dias_ate_coleta": (COLETA - d0).days, "movs": movs}, ensure_ascii=False) + "\n"); n += 1
json.dump({"registros": n, "movimentos": {str(c): {"nome": names[c], "ocorrencias": counts[c]} for c, _ in counts.most_common()}},
          open(names_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("ok", n, len(counts))
