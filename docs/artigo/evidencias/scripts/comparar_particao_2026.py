# Compara a partição 2026 de duas execuções Bronze. Imprime só contagens e datas (sem identificadores).
# Uso: python -I comparar_2026.py <run_root_antigo> <run_root_novo> [saida.json]
import gzip, json, sys
from collections import Counter
from pathlib import Path


def ler(root):
    root = Path(root)
    man = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    p = man["partitions"]["2026"]
    ids = {}
    for a in p["artifacts"]:
        d = json.loads(gzip.decompress((root / a["response"]).read_bytes()))
        for h in d["hits"]["hits"]:
            dt = str(h["_source"].get("dataAjuizamento") or "")
            ids[h["_id"]] = dt
    return ids


old, new = ler(sys.argv[1]), ler(sys.argv[2])
so_novo = set(new) - set(old)
so_antigo = set(old) - set(new)
ambos = set(old) & set(new)


def ymd(dt):
    return f"{dt[0:4]}-{dt[4:6]}-{dt[6:8]}" if len(dt) >= 8 else None


def mes(ids, sel):
    c = Counter(ids[i][0:6] for i in sel)
    return {f"{k[0:4]}-{k[4:6]}": v for k, v in sorted(c.items())}


corte_antigo = "20261018"
out = {
    "registros_antigo": len(old),
    "registros_novo": len(new),
    "em_ambos": len(ambos),
    "so_no_novo": len(so_novo),
    "so_no_antigo_sairam_do_indice": len(so_antigo),
    "dataAjuizamento_max_antigo": ymd(max(old.values())),
    "dataAjuizamento_max_novo": ymd(max(new.values())),
    "so_no_novo_ajuizados_ate_18_10": sum(1 for i in so_novo if new[i][0:8] <= corte_antigo),
    "so_no_novo_ajuizados_apos_18_10": sum(1 for i in so_novo if new[i][0:8] > corte_antigo),
    "data_ajuizamento_alterada_em_ambos": sum(1 for i in ambos if old[i] != new[i]),
    "so_no_novo_por_mes": mes(new, so_novo),
    "so_no_antigo_por_mes": mes(old, so_antigo),
    "novo_por_mes": mes(new, new),
}
s = json.dumps(out, ensure_ascii=False, indent=1)
print(s)
if len(sys.argv) > 3:
    Path(sys.argv[3]).write_text(s + "\n", encoding="utf-8")
