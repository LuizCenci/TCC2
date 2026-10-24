# Compara o ano do número CNJ (NNNNNNN-DD.AAAA.J.TR.OOOO) com o ano de dataAjuizamento (2019-2025).
# Saída só agregada; nenhum número é impresso ou gravado. Uso: python -I ano_numero_cnj.py <run_root> <saida.json>
import gzip, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
root = Path(sys.argv[1])
PRINC = {279, 283, 10943, 10944, 282, 278, 288, 272}
tab = defaultdict(Counter); dif = defaultdict(Counter); invalid = 0
for f in sorted(root.glob("responses/year=*/*.gz")):
    ano = int(f.parent.name.split("=")[1])
    if ano == 2026: continue
    for h in json.loads(gzip.decompress(f.read_bytes()))["hits"]["hits"]:
        s = h["_source"]; num = re.sub(r"\D", "", str(s.get("numeroProcesso") or ""))
        if len(num) != 20: invalid += 1; continue
        a_num = int(num[9:13]); c = (s.get("classe") or {}).get("codigo")
        movs = sorted((m for m in s.get("movimentos") or [] if m.get("dataHora")), key=lambda m: m["dataHora"])
        primeiro = "Documento(581)" if movs and movs[0].get("codigo") == 581 else "outro"
        t = "principal" if c in PRINC else ("carta" if c in (355, 335) else ("mpu" if c == 1268 else "outros"))
        rel = "mesmo_ano" if a_num == ano else ("numero_anterior" if a_num < ano else "numero_posterior")
        tab[f"{ano}|{t}|{primeiro}"][rel] += 1
        if a_num < ano: dif[f"{ano}|{t}"][min(ano - a_num, 10)] += 1
out = {"numeros_invalidos": invalid, "relacao_ano_numero_x_ajuizamento": {k: dict(v) for k, v in sorted(tab.items())},
       "anos_de_diferenca_quando_anterior": {k: dict(sorted(v.items())) for k, v in sorted(dif.items())}}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print("ok")
