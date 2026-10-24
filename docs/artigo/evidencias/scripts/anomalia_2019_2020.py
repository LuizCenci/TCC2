# Distribuição mensal 2019-2021 por tipo, para investigar picos (cartas 2020, principais 2019). Sem identificadores.
# Uso: python -I anomalia_2019_2020.py <extrato.jsonl.gz> <saida.json>
import gzip, json, sys
from collections import Counter, defaultdict
TIPO = {"principal": {279, 283, 10943, 10944, 282, 278, 288, 272}, "carta": {355, 335}, "mpu": {1268}}
mes = defaultdict(Counter); sede_pico = defaultdict(Counter); ass_carta = Counter(); primeiro_mov = defaultdict(Counter)
for line in gzip.open(sys.argv[1], "rt", encoding="utf-8"):
    r = json.loads(line)
    if r["ano"] > 2021: continue
    t = next((k for k, v in TIPO.items() if r["classe"] in v), "outros"); k = f"{r['ano']}-{r['mes']:02d}"
    mes[k][t] += 1
    if t == "carta" and r["ano"] == 2020: ass_carta.update(r["assuntos"]); sede_pico["carta_2020"][r["orgao"]] += 1
    if t == "principal" and r["ano"] == 2019: sede_pico["principal_2019"][r["orgao"]] += 1
    if r["movs"]: primeiro_mov[f"{t}_{r['ano']}"][r["movs"][0][0]] += 1
out = {"por_mes": {k: dict(v) for k, v in sorted(mes.items())}, "assuntos_cartas_2020": ass_carta.most_common(8),
       "orgaos_top": {k: v.most_common(8) for k, v in sede_pico.items()}, "primeiro_movimento": {k: v.most_common(4) for k, v in sorted(primeiro_mov.items())}}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
