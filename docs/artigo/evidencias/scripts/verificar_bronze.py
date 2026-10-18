# Verificação independente de uma execução Bronze: hashes, contagens, unicidade e datas.
# Não imprime identificadores de processos. Uso: python -I verificar_bronze.py <run_root> <saida.json>
import gzip, hashlib, json, sys
from collections import Counter
from pathlib import Path
root = Path(sys.argv[1]); man = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
out = {"run_id": man["run_id"], "status": man["status"], "catalog_version": man["catalog_version"],
       "catalog_source_hash": man["catalog_source_hash"], "config_hash": man["config_hash"],
       "collector_version": man.get("collector_version"), "finished_at": man.get("finished_at"), "anos": {}}
ids_global = Counter(); hash_ok = True
for ano, p in sorted(man["partitions"].items()):
    ids = Counter(); fora = 0; sem_data = 0; hits_total = 0; sha_bad = 0
    for a in p["artifacts"]:
        raw = (root / a["response"]).read_bytes()
        if hashlib.sha256(raw).hexdigest() != a["sha256"]: sha_bad += 1
        d = json.loads(gzip.decompress(raw))
        for h in d["hits"]["hits"]:
            hits_total += 1; ids[h["_id"]] += 1
            dt = str(h["_source"].get("dataAjuizamento") or "")
            if not dt: sem_data += 1
            elif not dt.startswith(ano): fora += 1
    ids_global.update(ids); hash_ok &= sha_bad == 0
    out["anos"][ano] = {"status": p["status"], "paginas": p["pages"], "registros_manifesto": p["records"],
        "registros_lidos": hits_total, "ids_unicos": len(ids), "ids_repetidos_no_ano": sum(c - 1 for c in ids.values() if c > 1),
        "total_api": p["total"]["value"], "relation": p["total"]["relation"], "data_fora_do_ano": fora, "sem_data": sem_data, "sha256_divergentes": sha_bad}
out["total_registros"] = sum(v["registros_lidos"] for v in out["anos"].values())
out["ids_unicos_global"] = len(ids_global)
out["ids_repetidos_entre_anos"] = sum(c - 1 for c in ids_global.values() if c > 1)
out["hashes_ok"] = hash_ok
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
