# Viabilidade de indicadores de tempo/movimentos e de agregação por comarca (2019-2025). Sem identificadores.
# Uso: python -I viabilidade_movimentos.py <extrato.jsonl.gz> <hierarquia_sgt.json> <catalogo.yaml> <saida.json>
import gzip, json, statistics, sys
from collections import Counter, defaultdict
import yaml
ext_path, hier_path, cat_path, out_path = sys.argv[1:5]
hier = json.load(open(hier_path, encoding="utf-8"))
cat = yaml.safe_load(open(cat_path, encoding="utf-8"))
core = {e["codigo"] for e in cat["assuntos"]}
estrita_a = core | {e["codigo"] for e in cat["extensoes"] if e["grupo"] == "especifica" and e["tipo"] == "assunto"}
estrita_c = {e["codigo"] for e in cat["extensoes"] if e["grupo"] == "especifica" and e["tipo"] == "classe"}
TIPO = {"principal": {279, 283, 10943, 10944, 282, 278, 288, 272}, "medida_protetiva": {1268, 15309, 12423},
        "incidente_cautelar": {305, 306, 307, 313, 280, 309, 1727, 1199, 333, 11793, 326, 14123, 11788, 1710, 325, 275, 419, 10967},
        "cooperacao_carta": {355, 335}}
def tipo(c): return next((k for k, v in TIPO.items() if c in v), "outros")
# Eventos definidos pela hierarquia oficial (SGT), não pelo nome.
path_codes = {int(c): {p["codigo"] for p in v["caminho"]} for c, v in hier.items()}
# Magistrado > Julgamento, exceto embargos de declaração, pronúncia, provimento e prejudicado (não encerram a instância).
JULG = {c for c, ps in path_codes.items() if 193 in ps} - {198, 200, 871, 10953, 237, 12459}
ARQ_DEF = {c for c, v in hier.items() for c in [int(c)] if v["nome_sgt"] and v["nome_sgt"].strip().lower() == "definitivo"} | {246}
BAIXA = {c for c, v in hier.items() for c in [int(c)] if v["nome_sgt"] and "baixa definitiva" in v["nome_sgt"].lower()}
TRANSITO = {848}
REABRE = {849, 893}                                             # Reativação, Desarquivamento
def km(durs):  # durs: list (t, evento:bool); retorna função de sobrevivência em pontos e mediana
    durs.sort(); n = len(durs); s = 1.0; i = 0; out = {}; med = None
    pts = {365: None, 730: None, 1095: None}
    while i < n:
        t = durs[i][0]; d = c = 0
        while i < n and durs[i][0] == t:
            d += durs[i][1]; c += 1; i += 1
        for p in pts:
            if pts[p] is None and t > p: pts[p] = s
        if d: s *= (1 - d / n_at_risk) if (n_at_risk := n - (i - c)) else 1
        if med is None and s <= 0.5: med = t
    for p in pts:
        if pts[p] is None: pts[p] = s
    return {"mediana_dias": med, "encerrados_ate_1a": round(1 - pts[365], 3), "ate_2a": round(1 - pts[730], 3), "ate_3a": round(1 - pts[1095], 3), "n": n, "eventos": sum(e for _, e in durs)}
stats = defaultdict(lambda: Counter()); km_data = defaultdict(list); nmov = defaultdict(list); qual = Counter()
sede = defaultdict(Counter); sede_km = defaultdict(list); ano_tipo = defaultdict(Counter)
for line in gzip.open(ext_path, "rt", encoding="utf-8"):
    r = json.loads(line); t = tipo(r["classe"]); a = set(r["assuntos"])
    estrita = bool(a & estrita_a) or r["classe"] in estrita_c
    movs = r["movs"]; codes = [c for c, _ in movs]
    nmov[t].append(len(movs)); qual["registros"] += 1
    qual["movimentos"] += len(movs); qual["mov_sem_data"] += sum(1 for _, d in movs if d is None)
    qual["mov_antes_ajuizamento"] += sum(1 for _, d in movs if d is not None and d < 0)
    first = lambda S: next((d for c, d in movs if c in S and d is not None and d >= 0), None)
    t_arq, t_jul, t_tra, t_bx = first(ARQ_DEF), first(JULG), first(TRANSITO), first(BAIXA)
    reab = any(c in REABRE for c in codes)
    k = (t, "estrita" if estrita else "ampliada_apenas")
    s = stats[k]; s["n"] += 1; s["com_arquivamento_definitivo"] += t_arq is not None; s["com_julgamento"] += t_jul is not None
    s["com_transito"] += t_tra is not None; s["com_baixa_definitiva"] += t_bx is not None; s["com_reabertura"] += reab
    fim = min([x for x in (t_arq, t_bx) if x is not None], default=None)
    obs = fim if fim is not None else r["dias_ate_coleta"]
    km_data[t].append((obs, fim is not None)); km_data[(t, r["ano"])].append((obs, fim is not None))
    ano_tipo[r["ano"]][t] += 1
    if t == "principal":
        sede[r["mun"]][r["ano"]] += 1; sede_km[r["mun"]].append((obs, fim is not None))
def q(v, p): v = sorted(v); return v[min(len(v) - 1, int(p * len(v)))]
tot = {m: sum(c.values()) for m, c in sede.items()}
sede_info = {"sedes": len(sede), "principais_por_sede_total": {"mediana": statistics.median(tot.values()), "min": min(tot.values()), "max": max(tot.values()),
             "p25": q(list(tot.values()), .25), "p75": q(list(tot.values()), .75)},
             "sedes_com_>=30_por_ano_em_todos_os_anos": sum(1 for m, c in sede.items() if all(c.get(y, 0) >= 30 for y in range(2019, 2026))),
             "sedes_com_>=100_no_periodo": sum(1 for v in tot.values() if v >= 100), "sedes_com_>=300_no_periodo": sum(1 for v in tot.values() if v >= 300),
             "sedes_com_>=50_encerramentos": sum(1 for v in sede_km.values() if sum(e for _, e in v) >= 50),
             "sedes_com_mediana_km_estimavel": sum(1 for v in sede_km.values() if km(list(v))["mediana_dias"] is not None)}
out = {"definicoes": {"julgamento_codigos": sorted(JULG), "arquivamento_definitivo_codigos": sorted(ARQ_DEF), "baixa_definitiva_codigos": sorted(BAIXA),
                      "transito": sorted(TRANSITO), "reabertura": sorted(REABRE), "fim": "primeiro arquivamento definitivo ou baixa definitiva; sem fim = censurado na data da coleta (18/10/2026)"},
       "qualidade_datas": dict(qual),
       "eventos_por_tipo_e_serie": {f"{k[0]}|{k[1]}": {**dict(v), **{f"pct_{x[4:]}": round(100 * v[x] / v["n"], 1) for x in list(v) if x.startswith("com_")}} for k, v in sorted(stats.items())},
       "km_por_tipo": {k: km(list(v)) for k, v in km_data.items() if isinstance(k, str)},
       "km_principal_por_ano": {str(k[1]): km(list(v)) for k, v in sorted(km_data.items(), key=str) if isinstance(k, tuple) and k[0] == "principal"},
       "movimentos_por_tipo": {k: {"mediana": statistics.median(v), "p25": q(v, .25), "p75": q(v, .75)} for k, v in nmov.items()},
       "procedimentos_por_ano_e_tipo": {str(k): dict(v) for k, v in sorted(ano_tipo.items())}, "sedes": sede_info}
json.dump(out, open(out_path, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
