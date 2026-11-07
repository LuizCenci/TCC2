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


def test_colapso_e_subcontagem(pasta, conn_banco_modulo):
    for nome in ("agg_volume.csv", "agg_mpu.csv"):
        assert "mesorregiao_id" not in _ler(pasta, nome)[0]
    db = conn_banco_modulo.execute(
        "SELECT coalesce(sum(n),0) FROM gold.agg_volume WHERE ano_ajuizamento=%s", (ANO,)
    ).fetchone()[0]
    assert 0 < db < 10  # soma sintética por série; cada linha colapsada < 5 sai suprimida
    man = json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
    assert set(man["agregacoes_exportacao"]) == {"agg_volume", "agg_mpu"}
    assert man["regras_supressao"]["agg_mpu"]["limite"] == 5


def test_subcontagem_no_csv(conn_banco_modulo, tmp_path):
    from datajud_tcc.gold.metodos import exportacao, supressao
    r = supressao.aplicar([{"ano": 1, "n": 50, "n_flagrante": 2, "n_preventiva": 40}], limite=5,
                          colunas_grupo=("ano",), colunas_valor=(),
                          colunas_contagem=exportacao.CONTAGENS["agg_cautelar"])
    assert r[0]["n_flagrante"] is None and r[0]["n_preventiva"] == 40 and r[0]["suprimido_parcial"]
    p = exportacao.exportar(conn_banco_modulo, tmp_path)
    for rr in _ler(p, "agg_cautelar.csv"):
        if rr["suprimido_parcial"] == "true":
            assert "" in (rr["n_flagrante"], rr["n_preventiva"], rr["n_liberdade_provisoria_concedida"])


# ------------------------------------------------------------------ estratos sintéticos (ano 2090/2091)
@pytest.fixture(scope="module")
def sintetica(conn_banco_modulo, tmp_path_factory):
    c = conn_banco_modulo
    aplicar_esquema_gold(c)
    for meso, n in ((1, 20), (2, 30)):
        c.execute("INSERT INTO gold.agg_volume (pergunta, ano_ajuizamento, ano_parcial,"
                  " mes_ajuizamento, tipo_procedimento, mesorregiao_id, serie, n)"
                  " VALUES ('QT9', 2090, false, 3, 'MPU', %s, 'ampliada', %s)", (meso, n))
    for meso, vals in ((1, (20, 10, 6, 8, 6, 5)), (2, (30, 10, 7, 9, 7, 6))):
        c.execute("INSERT INTO gold.agg_mpu (pergunta, ano_ajuizamento, ano_parcial, mesorregiao_id,"
                  " orgao_especializado, serie, n, n_com_decisao, n_deferimento, n_parcial,"
                  " n_indeferimento, n_revogadas) VALUES ('QT9', 2090, false, %s, false,"
                  " 'ampliada', %s, %s, %s, %s, %s, %s)", (meso, *vals))
    # conjunto aditivo: n_deferimento=2 (< 5) arrasta a menor das demais (n_parcial=20)
    c.execute("INSERT INTO gold.agg_mpu (pergunta, ano_ajuizamento, ano_parcial, mesorregiao_id,"
              " orgao_especializado, serie, n, n_com_decisao, n_deferimento, n_parcial,"
              " n_indeferimento, n_revogadas) VALUES ('QT9', 2091, false, 1, false,"
              " 'ampliada', 100, 50, 2, 20, 28, 9)")
    # cautelar com subcontagem pequena (n >= 5): deve gerar suprimido_parcial
    c.execute("INSERT INTO gold.agg_cautelar (pergunta, ano_ajuizamento, ano_parcial,"
              " tipo_procedimento, categoria, serie, n, n_flagrante, n_preventiva,"
              " n_liberdade_provisoria_concedida) VALUES ('QT9', 2090, false, 'ACAO_PENAL',"
              " 'x', 'ampliada', 40, 2, 30, 8)")
    # tempo: n_eventos < 5 -> estimativas vazias; n e n_eventos arredondados ao múltiplo de 10
    ins_t = ("INSERT INTO gold.agg_tempo (pergunta, marco, tipo_procedimento, serie, estrato,"
             " valor_estrato, n, n_eventos, estimavel, mediana_dias, mediana_alcancada, ic95_inf,"
             " ic95_sup, pct_evento_ate_2, pct_evento_ate_30, pct_evento_ate_365,"
             " pct_evento_ate_730) VALUES ('QT9', %s, 'MPU', 'ampliada', 'total', 'total', %s, %s,"
             " true, 5.0, true, 4.0, 6.0, 1.0, 2.0, 3.0, 4.0)")
    c.execute(ins_t, ("m_pouco", 47, 3))
    c.execute(ins_t, ("m_muito", 15, 12))
    c.execute("INSERT INTO gold.agg_desfecho (pergunta, tipo_procedimento, serie, variante, estrato,"
              " valor_estrato, desfecho, n, n_desfecho, estimavel, ia_365, ia_730, ia_1095, ia_1825)"
              " VALUES ('QT9', 'ACAO_PENAL', 'ampliada', 'principal', 'total', 'total',"
              " 'CONDENACAO', 45, 2, true, 1.0, 2.0, 3.0, 4.0)")
    return exportar(c, tmp_path_factory.mktemp("pub_sint"))


def test_somas_exportadas_iguais_as_do_banco(sintetica, conn_banco_modulo):
    for tabela, cols in (("agg_volume", ("n",)),
                         ("agg_mpu", ("n", "n_com_decisao", "n_deferimento", "n_parcial",
                                      "n_indeferimento", "n_revogadas"))):
        exp = [r for r in _ler(sintetica, f"{tabela}.csv") if r["ano_ajuizamento"] == "2090"]
        assert len(exp) == 1 and exp[0]["suprimido"] == "false"
        for c in cols:
            db = conn_banco_modulo.execute(
                f"SELECT sum({c}) FROM gold.{tabela} WHERE ano_ajuizamento=2090"  # noqa: S608
            ).fetchone()[0]
            assert int(exp[0][c]) == db, (tabela, c)


def test_mpu_conjunto_aditivo_e_parcial_incondicional(sintetica):
    r = [x for x in _ler(sintetica, "agg_mpu.csv") if x["ano_ajuizamento"] == "2091"][0]
    assert r["n_deferimento"] == "" and r["n_parcial"] == ""
    assert r["n_indeferimento"] == "28" and r["suprimido_parcial"] == "true"
    c = [x for x in _ler(sintetica, "agg_cautelar.csv") if x["ano_ajuizamento"] == "2090"][0]
    assert c["n_flagrante"] == "" and c["n_preventiva"] == "30" and c["suprimido_parcial"] == "true"


def test_tempo_com_poucos_eventos_sem_estimativas(sintetica):
    rows = {r["marco"]: r for r in _ler(sintetica, "agg_tempo.csv") if r["pergunta"] == "QT9"}
    p = rows["m_pouco"]
    for c in ("n_eventos", "mediana_dias", "mediana_alcancada", "ic95_inf", "ic95_sup",
              "pct_evento_ate_2", "pct_evento_ate_30", "pct_evento_ate_365", "pct_evento_ate_730"):
        assert p[c] == "", c
    assert p["suprimido_parcial"] == "true" and p["n"] == "50"
    m = rows["m_muito"]
    assert (m["n"], m["n_eventos"]) == ("20", "10") and m["mediana_dias"] == "5.0"
    d = [r for r in _ler(sintetica, "agg_desfecho.csv") if r["pergunta"] == "QT9"][0]
    assert d["n"] == "50" and d["n_desfecho"] == "" and d["ia_365"] == "" and d["ia_1825"] == ""


def test_tempo_e_desfecho_arredondados_a_10(sintetica):
    for nome, cols in (("agg_tempo.csv", ("n", "n_eventos")), ("agg_desfecho.csv", ("n", "n_desfecho"))):
        for r in _ler(sintetica, nome):
            for c in cols:
                assert r[c] == "" or int(r[c]) % 10 == 0, (nome, c, r[c])
    man = json.loads((sintetica / "manifesto.json").read_text(encoding="utf-8"))
    assert man["arredondamento"] == {"tabelas": ["agg_tempo", "agg_desfecho"], "base": 10}


def test_pasta_existente_nao_e_sobrescrita(conn_banco_modulo, tmp_path):
    p1 = exportar(conn_banco_modulo, tmp_path)
    p2 = exportar(conn_banco_modulo, tmp_path)
    assert p1 != p2 and p1.exists() and p2.exists() and p2.name.startswith(p1.name + "_")
    assert (p1 / "manifesto.json").exists() and (p2 / "manifesto.json").exists()
