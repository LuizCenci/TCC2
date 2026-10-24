# Classe dos procedimentos principais por ano e pelo 1º movimento (581 Documento x outro). Sem identificadores.
# Uso: python -I classe_por_ano_inicio.py <extrato.jsonl.gz> <saida.json>
import gzip, json, sys
from collections import Counter, defaultdict
PRINC = {279, 283, 10943, 10944, 282, 278, 288, 272}
t = defaultdict(Counter); tram = Counter()
for line in gzip.open(sys.argv[1], "rt", encoding="utf-8"):
    r = json.loads(line)
    if r["classe"] not in PRINC: continue
    ini = "581" if r["movs"] and r["movs"][0][0] == 581 else "outro"
    t[f"{r['ano']}|{ini}"][r["classe"]] += 1
    if any(c == 14999 for c, _ in r["movs"]): tram[r["ano"]] += 1
json.dump({"classes": {k: dict(v.most_common()) for k, v in sorted(t.items())}, "com_tramitacao_direta_mp_policia_14999": dict(sorted(tram.items()))},
          open(sys.argv[2], "w", encoding="utf-8", newline="\n"), indent=1)
