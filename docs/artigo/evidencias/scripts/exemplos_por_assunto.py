# Gera exemplos e perfis por código do catálogo a partir da Bronze (2019-2025), sem identificadores.
# Não usa numeroProcesso, id nem datas completas: só ano-mês e dias desde o ajuizamento.
# Uso: python -I exemplos_por_assunto.py <run_root> <catalogo.yaml> <saida.md> <saida.json>
import gzip, json, random, statistics, sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import yaml

root, cat_path, out_md, out_json = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
cat = yaml.safe_load(cat_path.read_text(encoding="utf-8"))
codes = []  # (tabela, codigo, grupo, descricao)
for e in cat["assuntos"]: codes.append(("assunto", e["codigo"], "nucleo_pvd", e["descricao"]))
for e in cat["extensoes"]: codes.append((e["tipo"], e["codigo"], e["grupo"], e["descricao"]))
for e in cat["marcadores_silver"]: codes.append(("assunto", e["codigo"], "marcador", e["descricao"]))
KEY = ("protetiva", "concess", "deferid", "indeferid", "revoga", "senten", "arquiv", "baixa", "denúncia", "recebid", "extin", "condena", "absolv", "evolução", "apens", "redistrib")

def dt(s):
    s = str(s)
    if len(s) == 14 and s.isdigit(): return datetime.strptime(s, "%Y%m%d%H%M%S")
    try: return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError: return None

recs = []
for f in sorted(root.glob("responses/year=*/*.gz")):
    ano = f.parent.name.split("=")[1]
    if ano == "2026": continue
    for h in json.loads(gzip.decompress(f.read_bytes()))["hits"]["hits"]:
        recs.append(h["_source"])

proc = Counter(r.get("numeroProcesso") for r in recs)  # só para contagem de multiplicidade; nunca impresso
mov_names = Counter(); n_mov = []
for r in recs:
    ms = r.get("movimentos") or []; n_mov.append(len(ms))
    for m in ms: mov_names[m.get("nome")] += 1
glob = {"registros_2019_2025": len(recs), "numeros_processo_distintos": len(proc),
        "numeros_com_mais_de_um_registro": sum(1 for c in proc.values() if c > 1),
        "registros_sem_movimentos": sum(1 for n in n_mov if n == 0), "mediana_movimentos": statistics.median(n_mov),
        "movimentos_ligacao": {k: v for k, v in mov_names.items() if k and any(t in k.lower() for t in ("apens", "associa", "evolução", "vincula", "reuni", "conex"))}}

def has(r, tab, code):
    if tab == "classe": return (r.get("classe") or {}).get("codigo") == code
    return any(a.get("codigo") == code for a in r.get("assuntos") or [] if isinstance(a, dict))

def flat_assuntos(r):
    return [(a.get("codigo"), a.get("nome")) for a in r.get("assuntos") or [] if isinstance(a, dict)]

def example(r):
    d0 = dt(r.get("dataAjuizamento"))
    ms = sorted((m for m in r.get("movimentos") or [] if dt(m.get("dataHora"))), key=lambda m: dt(m["dataHora"]))
    pick = ms[:2] + [m for m in ms[2:-2] if any(t in (m.get("nome") or "").lower() for t in KEY)][:5] + ms[-2:] if len(ms) > 4 else ms
    seen, linhas = set(), []
    for m in pick:
        if id(m) in seen: continue
        seen.add(id(m)); dias = (dt(m["dataHora"]) - d0).days if d0 else None
        comp = "; ".join(c.get("nome", "") for c in m.get("complementosTabelados") or [] if c.get("nome"))
        nome = m.get("nome") or ""
        # O nome "Medida protetiva" é compartilhado por concessão, não-concessão e revogação: mostrar o código.
        rotulo = f"{nome} [mov. {m.get('codigo')}]" if "rotetiva" in nome else nome
        linhas.append(f"d+{dias} {rotulo}" + (f" ({comp})" if comp else ""))
    o = r.get("orgaoJulgador") or {}
    return {"ano_mes": d0.strftime("%Y-%m") if d0 else None, "classe": f"{r['classe'].get('codigo')} {r['classe'].get('nome')}",
            "assuntos": [f"{c} {n}" for c, n in flat_assuntos(r)], "orgao": o.get("nome"), "n_movimentos": len(r.get("movimentos") or []), "movimentos": linhas}

rng = random.Random(20261023)
perfil, md = {}, []
for tab, code, grupo, desc in codes:
    sub = [r for r in recs if has(r, tab, code)]
    cls = Counter(f"{r['classe'].get('codigo')} {r['classe'].get('nome')}" for r in sub)
    co = Counter(f"{c} {n}" for r in sub for c, n in set(flat_assuntos(r)) if not (tab == "assunto" and c == code))
    jv = sum(1 for r in sub if "VIOLÊNCIA DOMÉSTICA" in ((r.get("orgaoJulgador") or {}).get("nome") or "").upper())
    nm = [len(r.get("movimentos") or []) for r in sub]
    perfil[f"{tab}:{code}"] = {"grupo": grupo, "descricao": desc, "registros": len(sub), "classes_top": cls.most_common(5), "coassuntos_top": co.most_common(6),
                               "pct_orgao_jvdfm": round(100 * jv / len(sub), 1) if sub else None, "mediana_movimentos": statistics.median(nm) if nm else None}
    p = perfil[f"{tab}:{code}"]
    md.append(f"### {tab} {code} — {desc}  \n*grupo: {grupo}; registros 2019–2025: {len(sub):,}*".replace(",", "."))
    if not sub: md.append("\nSem registros no recorte.\n"); continue
    md.append(f"\n- Classes mais frequentes: " + "; ".join(f"{k} ({v:,})".replace(",", ".") for k, v in p["classes_top"][:3]))
    md.append("- Assuntos que mais aparecem junto: " + ("; ".join(f"{k} ({v:,})".replace(",", ".") for k, v in p["coassuntos_top"][:4]) or "nenhum"))
    md.append(f"- Em Juizado de Violência Doméstica: {p['pct_orgao_jvdfm']}% · mediana de movimentos: {p['mediana_movimentos']}\n")
    for i, r in enumerate(rng.sample(sub, min(3, len(sub))), 1):
        e = example(r)
        md.append(f"**Exemplo {i}** — {e['ano_mes']} · classe {e['classe']} · {e['orgao']} · {e['n_movimentos']} movimentos  \nAssuntos: {' | '.join(e['assuntos'])}  \nMovimentos (dias desde o ajuizamento): {' → '.join(e['movimentos'])}\n")
out_md.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
json.dump({"global": glob, "perfil": perfil}, open(out_json, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps(glob, ensure_ascii=False, indent=1))
