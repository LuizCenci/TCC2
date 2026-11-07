import csv
import hashlib
import json
import time
from datetime import datetime

import pytest

from datajud_tcc.gold.construcao import executar_transformacoes
from datajud_tcc.gold.esquema import aplicar_esquema_gold
from datajud_tcc.gold.metodos.exportacao import exportar
from datajud_tcc.gold.metodos.sobrevivencia import construir_agg_desfecho, construir_agg_tempo
from datajud_tcc.gold.metodos.taxas import construir_agg_taxa
from datajud_tcc.gold.referencias import carregar_referencias
from datajud_tcc.gold.territorio import carregar_territorio
from datajud_tcc.silver.esquema import aplicar_esquema
from gold_dados import inserir_execucao, inserir_registro, utc

pytestmark = [pytest.mark.banco, pytest.mark.gold_lento]
ANO = 2041
PROIBIDAS = {"registro_id", "numero_processo", "api_id"}


@pytest.fixture(scope="module")
def pasta(conn_banco_modulo, tmp_path_factory):
    conn = conn_banco_modulo
    aplicar_esquema(conn)
    aplicar_esquema_gold(conn)
    carregar_territorio(conn)
    carregar_referencias(conn)
    inserir_execucao(conn, "T50", utc(2043, 6, 1), [ANO])
    for i in range(3):
        inserir_registro(conn, "T50", f"ex-{i}", ano=ANO, classe=282, orgao=1,
                         municipio=4106902, ajuizamento=datetime(ANO, 3, 10, 9),
                         assuntos=(10949,), numero=f"50{i:02d}")
    executar_transformacoes(conn)
    construir_agg_taxa(conn)
    construir_agg_tempo(conn)
    construir_agg_desfecho(conn)
    t0 = time.time()
    p = exportar(conn, tmp_path_factory.mktemp("pub"))
    tam = sum(f.stat().st_size for f in p.iterdir())
    print(f"exportar: {time.time() - t0:.1f}s, {tam / 1e6:.2f} MB")
    return p


def _ler(p, nome):
    with open(p / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_exportacao_sem_identificadores_e_suprimida(pasta):
    for f in pasta.glob("*.csv"):
        with open(f, encoding="utf-8", newline="") as h:
            assert not PROIBIDAS & set(next(csv.reader(h)))
    sint = [r for r in _ler(pasta, "agg_volume.csv") if r["ano_ajuizamento"] == str(ANO)]
    assert sint and all(r["n"] == "" and r["suprimido"] == "true" for r in sint)
    for nome, lim in (("agg_volume.csv", 5), ("agg_categoria.csv", 5), ("agg_taxa.csv", 5)):
        for r in _ler(pasta, nome):
            if r["suprimido"] == "true":
                assert r["n"] == ""
            else:
                assert int(r["n"]) >= lim
    man = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    assert man["versao_regras"] and man["data_corte_max"] and man["gerado_em"]
    assert len(man["arquivos"]) == 12
    for a in man["arquivos"]:
        assert hashlib.sha256((pasta / a["arquivo"]).read_bytes()).hexdigest() == a["sha256"]
