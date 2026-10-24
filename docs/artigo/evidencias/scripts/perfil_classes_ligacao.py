# Perfil de classes x grupo de inclusão, sinais de ligação entre processos e medidas protetivas (2019-2025).
# Leitura em streaming da Bronze; não imprime identificadores. Uso: python -I perfil_classes_ligacao.py <run_root> <catalogo.yaml> <saida.json>
import gzip, json, sys
from collections import Counter, defaultdict
from pathlib import Path
import yaml
root, cat = Path(sys.argv[1]), yaml.safe_load(Path(sys.argv[2]).read_text(encoding="utf-8"))
core = {e["codigo"] for e in cat["assuntos"]}
ext = {g: {"assunto": set(), "classe": set()} for g in ("especifica", "ambigua", "secundaria")}
for e in cat["extensoes"]: ext[e["grupo"]][e["tipo"]].add(e["codigo"])
TIPO = {  # agrupamento de classes proposto para a Silver
 "principal": {279, 283, 10943, 10944, 282, 278, 288, 272},
 "medida_protetiva": {1268, 15309, 12423},
 "incidente_cautelar": {305, 306, 307, 313, 280, 309, 1727, 1199, 333, 11793, 326, 14123, 11788, 1710, 325, 275, 419, 10967},
 "cooperacao_carta": {355, 335},
 "civel": {7, 156},
}
def tipo(c):
    for k, v in TIPO.items():
        if c in v: return k
    return "outros"
def grupo(r):
    a = {x.get("codigo") for x in r.get("assuntos") or [] if isinstance(x, dict)}; c = (r.get("classe") or {}).get("codigo")
    if a & core: return "1_nucleo"
    if a & ext["especifica"]["assunto"] or c in ext["especifica"]["classe"]: return "2_especifica"
    if a & ext["ambigua"]["assunto"]: return "3_ambigua"
    return "4_secundaria"
cross = defaultdict(Counter); outros = Counter(); n = 0
apens_comp = Counter(); evol_comp = Counter(); mp = Counter(); benef = Counter(); medidas = Counter()
for f in sorted(root.glob("responses/year=*/*.gz")):
    if f.parent.name == "year=2026": continue
    for h in json.loads(gzip.decompress(f.read_bytes()))["hits"]["hits"]:
        r = h["_source"]; n += 1; c = (r.get("classe") or {}).get("codigo"); t = tipo(c)
        cross[grupo(r)][t] += 1
        if t == "outros": outros[f"{c} {(r.get('classe') or {}).get('nome')}"] += 1
        ms = r.get("movimentos") or []
        tem_mp = False
        for m in ms:
            nome = m.get("nome") or ""; comps = [x.get("nome") for x in m.get("complementosTabelados") or []]
            if nome == "Apensamento": apens_comp[len(comps) > 0] += 1
            if nome.startswith("Evolu"): evol_comp.update(comps)
            if nome in ("Medida protetiva", "Prorrogação de Medida Protetiva") or "protetiva" in nome.lower():
                tem_mp = True; mp[nome] += 1
                for x in comps:
                    if x and x.startswith(("A mulher", "A criança", "O idoso", "A pessoa", "O homem")): benef[x] += 1
                    elif x: medidas[x] += 1
        if c == 1268: mp["_classe1268_total"] += 1; mp["_classe1268_com_movimento_protetiva"] += tem_mp
out = {"registros": n, "grupo_x_tipo_classe": {g: dict(v) for g, v in sorted(cross.items())},
       "tipo_classe_total": dict(sum(cross.values(), Counter())), "outros_top": outros.most_common(15),
       "apensamento_com_complemento": {str(k): v for k, v in apens_comp.items()}, "evolucao_classe_complementos": evol_comp.most_common(10),
       "movimentos_protetiva": dict(mp), "beneficiario": benef.most_common(10), "medidas_top": medidas.most_common(15), "agrupamento_classes": {k: sorted(v) for k, v in TIPO.items()}}
json.dump(out, open(sys.argv[3], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
