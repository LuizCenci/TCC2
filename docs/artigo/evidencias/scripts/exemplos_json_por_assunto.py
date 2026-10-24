# Exemplos por código no formato JSON original do hit retornado pela API (2019-2025) e inventário de campos.
# Exemplos = os 3 primeiros registros de cada código na ordem da coleta (partição 2019 primeiro; dentro dela, id ascendente).
# Mascarados por decisão do autor (23-24/10/2026): _id, sort, _source.id, _source.numeroProcesso.
# Uso: python -I exemplos_json_por_assunto.py <run_root> <catalogo.yaml> <saida.md> <campos.json>
import gzip, json, sys
from collections import Counter, defaultdict
from pathlib import Path
import yaml
root, cat_path, out_md, out_campos = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
cat = yaml.safe_load(cat_path.read_text(encoding="utf-8"))
codes = [("assunto", e["codigo"], "nucleo_pvd", e["descricao"]) for e in cat["assuntos"]]
codes += [(e["tipo"], e["codigo"], e["grupo"], e["descricao"]) for e in cat["extensoes"]]
codes += [("assunto", e["codigo"], "marcador", e["descricao"]) for e in cat["marcadores_silver"]]
MASK = "<omitido>"

# Inventário de campos: caminho -> registros em que aparece não nulo; tipos observados.
presente, tipos, n_total = Counter(), defaultdict(Counter), 0
def inventario(x, path, vistos):
    # Conta cada caminho no máximo uma vez por registro: lista não vazia ou escalar não nulo.
    if isinstance(x, dict):
        for k, v in x.items(): inventario(v, f"{path}.{k}" if path else k, vistos)
        return
    if isinstance(x, list):
        if x and path not in vistos: vistos.add(path); presente[path] += 1; tipos[path]["list"] += 1
        for v in x: inventario(v, path + "[]", vistos)
        return
    if x is not None and path not in vistos:
        vistos.add(path); presente[path] += 1; tipos[path][type(x).__name__] += 1

def has(s, tab, code):
    if tab == "classe": return (s.get("classe") or {}).get("codigo") == code
    return any(a.get("codigo") == code for a in s.get("assuntos") or [] if isinstance(a, dict))
def mascarar(h):
    h = json.loads(json.dumps(h)); h["_id"] = MASK
    if "sort" in h: h["sort"] = [MASK]
    h["_source"]["id"] = MASK; h["_source"]["numeroProcesso"] = MASK
    return h
def formatar(h):
    # JSON válido e fiel; cada movimento em uma linha para manter o arquivo legível.
    s = h["_source"]; movs = s.get("movimentos") or []
    corpo = {k: v for k, v in h.items() if k != "_source"}
    fonte = {k: v for k, v in s.items() if k != "movimentos"}
    linhas = ["{"]
    for k, v in corpo.items(): linhas.append(f'  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},')
    linhas.append('  "_source": {')
    for k, v in fonte.items(): linhas.append(f'    {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)},')
    linhas.append('    "movimentos": [')
    linhas += [f'      {json.dumps(m, ensure_ascii=False)}' + ("," if i < len(movs) - 1 else "") for i, m in enumerate(movs)]
    linhas += ["    ]", "  }", "}"]
    return "\n".join(linhas)

def resumo(h):
    s = h["_source"]; n = len(s.get("movimentos") or [])
    return (f"<details>\n<summary><b>{{titulo}}</b> — classe {s['classe'].get('codigo')} {s['classe'].get('nome')} · "
            f"{s['orgaoJulgador'].get('nome')} · ajuizamento {str(s.get('dataAjuizamento'))[:8]} · {n} movimentos</summary>\n\n"
            f"```json\n{formatar(mascarar(h))}\n```\n\n</details>\n")
primeiros = {(t, c): [] for t, c, _, _ in codes}; totais = Counter()
for f in sorted(root.glob("responses/year=*/*.gz"), key=lambda p: (p.parent.name, p.name)):
    ano = f.parent.name.split("=")[1]
    for h in json.loads(gzip.decompress(f.read_bytes()))["hits"]["hits"]:
        n_total += 1; vistos = set(); inventario(h, "", vistos)
        if ano == "2026": continue
        for t, c, _, _ in codes:
            if has(h["_source"], t, c):
                totais[(t, c)] += 1
                if len(primeiros[(t, c)]) < 3: primeiros[(t, c)].append(h)
md = []
for tab, code, grupo, desc in codes:
    sub = primeiros[(tab, code)]
    total = f"{totais[(tab, code)]:,}".replace(",", ".")
    md.append(f"## {tab} {code} — {desc}\n\n*grupo: {grupo}; registros 2019–2025: {total}*\n")
    if not sub: md.append("Sem registros no recorte.\n"); continue
    for i, h in enumerate(sub, 1): md.append(resumo(h).replace("{titulo}", f"Registro {i}"))
out_md.write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
campos = {p: {"registros_com_valor": presente[p], "pct": round(100 * presente[p] / n_total, 2), "tipos": dict(tipos[p])} for p in sorted(set(presente) | set(tipos))}
json.dump({"registros_analisados": n_total, "campos": campos}, open(out_campos, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
