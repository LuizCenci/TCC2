# Testa se a API aceita filtro por dataHoraUltimaAtualizacao (size=0; só contagens e agregações).
# Uso (raiz do projeto): python -I teste_ultima_atualizacao.py <dir_scripts> <saida.json>
import json, sys, time
from pathlib import Path
sys.path.insert(0, "src"); sys.path.insert(0, sys.argv[1])
from q import search
from datajud_tcc.catalog import Catalog
from datajud_tcc.query import _thematic_filter
cat = Catalog.load(Path("config/catalogs/tjpr_vcm_2026-10-18.yaml"))
base = [{"term": {"grau.keyword": "G1"}}, _thematic_filter(cat)]
def rng(campo, gte, lt): return {"range": {campo: {"gte": gte, "lt": lt}}}
testes = {
 "A_iso_completo_out2026": base + [rng("dataHoraUltimaAtualizacao", "2026-10-01T00:00:00.000Z", "2026-11-01T00:00:00.000Z")],
 "B_so_data_out2026": base + [rng("dataHoraUltimaAtualizacao", "2026-10-01", "2026-11-01")],
 "C_formato_ajuizamento_out2026": base + [rng("dataHoraUltimaAtualizacao", "20261001000000", "20261101000000")],
 "D_iso_out2026_ajuizados_2019_2025": base + [rng("dataHoraUltimaAtualizacao", "2026-10-01T00:00:00.000Z", "2026-11-01T00:00:00.000Z"),
                                               rng("dataAjuizamento", "20190101000000", "20260101000000")],
}
out = {}
for nome, filtros in testes.items():
    body = {"size": 0, "track_total_hits": True, "query": {"bool": {"filter": filtros}}}
    if nome.startswith("A"):
        body["aggs"] = {"min": {"min": {"field": "dataHoraUltimaAtualizacao"}}, "max": {"max": {"field": "dataHoraUltimaAtualizacao"}},
                        "semana": {"date_histogram": {"field": "dataHoraUltimaAtualizacao", "calendar_interval": "week"}}}
    st, d = search(body)
    out[nome] = {"status": st, "total": (d.get("hits") or {}).get("total"), "took": d.get("took"),
                 "aggs": d.get("aggregations"), "erro": str(d.get("error"))[:300] if d.get("error") else None}
    print(nome, out[nome]["status"], out[nome]["total"], out[nome]["erro"], flush=True); time.sleep(3)
json.dump({"consultado_em": time.strftime("%Y-%m-%dT%H:%M:%S"), "testes": out}, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
