# Conta códigos de movimentos de medida protetiva (2019-2025) e o tempo até o primeiro, por código. Sem identificadores.
# Uso: python -I codigos_movimento_mp.py <run_root> <saida.json>
import gzip, json, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
root = Path(sys.argv[1])
def dt(s):
    s = str(s)
    if len(s) == 14 and s.isdigit(): return datetime.strptime(s, "%Y%m%d%H%M%S")
    try: return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError: return None
cod = Counter(); cod_1268 = Counter(); proc_com = Counter(); dias = defaultdict(list); n1268 = 0; nomes = {}
for f in sorted(root.glob("responses/year=*/*.gz")):
    if f.parent.name == "year=2026": continue
    for h in json.loads(gzip.decompress(f.read_bytes()))["hits"]["hits"]:
        r = h["_source"]; is1268 = (r.get("classe") or {}).get("codigo") == 1268; n1268 += is1268
        d0 = dt(r.get("dataAjuizamento")); primeiros = {}
        for m in r.get("movimentos") or []:
            nome = m.get("nome") or ""
            if "rotetiva" not in nome: continue
            c = m.get("codigo"); nomes[c] = nome; cod[c] += 1
            if is1268: cod_1268[c] += 1
            t = dt(m.get("dataHora"))
            if t and (c not in primeiros or t < primeiros[c]): primeiros[c] = t
        if is1268:
            for c, t in primeiros.items():
                proc_com[c] += 1
                if d0: dias[c].append((t - d0).days)
def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))] if v else None
out = {"classe1268_registros": n1268,
       "movimentos": {str(c): {"nome": nomes[c], "ocorrencias_total": cod[c], "ocorrencias_em_1268": cod_1268[c], "registros_1268_com_o_movimento": proc_com[c],
                     "dias_ate_primeiro_mediana": statistics.median(dias[c]) if dias[c] else None, "dias_p25": q(dias[c], .25), "dias_p75": q(dias[c], .75),
                     "dias_negativos": sum(1 for x in dias[c] if x < 0)} for c in sorted(cod, key=lambda k: -cod[k])}}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
