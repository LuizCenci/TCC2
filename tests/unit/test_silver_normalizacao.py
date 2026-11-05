"""Testes da normalização pura de um registro (dados sintéticos)."""
import hashlib
import json
from datetime import datetime, timezone

from datajud_tcc.silver.normalizacao import normalizar_hit


def hit(**src):
    base = {
        "id": "ID-SINTETICO",
        "numeroProcesso": "00012345620238160001",
        "tribunal": "TJPR",
        "grau": "G1",
        "nivelSigilo": 0,
        "classe": {"codigo": 100, "nome": "Classe X"},
        "assuntos": [{"codigo": 1, "nome": "A1"}],
        "dataAjuizamento": "20230725154120",
        "dataHoraUltimaAtualizacao": "2025-07-11T10:00:00.000Z",
        "@timestamp": "2025-07-12T10:00:00.000Z",
        "orgaoJulgador": {"codigo": 5, "nome": "Vara", "codigoMunicipioIBGE": 4106902},
        "sistema": {"codigo": 1, "nome": "PROJUDI"},
        "formato": {"codigo": 1, "nome": "Eletrônico"},
        "movimentos": [],
    }
    base.update(src)
    return {"_id": "API-1", "_index": "i", "_score": None, "_source": base, "sort": [1]}


def norm(h):
    return normalizar_hit(h, run_id="run1", ano=2023, pagina=3)


def test_campos_basicos_e_hash():
    h = hit()
    n = norm(h)
    r = n.registro
    assert r["run_id"] == "run1" and r["api_id"] == "API-1"
    assert r["ano_particao"] == 2023 and r["pagina"] == 3
    assert r["classe_codigo"] == 100 and r["orgao_codigo"] == 5
    assert r["municipio_sede_ibge"] == 4106902
    assert r["n_movimentos"] == 0
    assert r["indexado_em"] == datetime(2025, 7, 12, 10, tzinfo=timezone.utc)
    esperado = hashlib.sha256(
        json.dumps(h["_source"], sort_keys=True, ensure_ascii=False,
                   separators=(",", ":")).encode("utf-8")).hexdigest()
    assert r["hash_source"] == esperado


def test_data_ajuizamento_formato_tjpr():
    r = norm(hit()).registro
    assert r["data_ajuizamento_original"] == "20230725154120"
    assert r["data_ajuizamento"] == datetime(2023, 7, 25, 15, 41, 20)
    assert r["data_ajuizamento"].tzinfo is None


def test_data_ajuizamento_invalida_vira_nula():
    r = norm(hit(dataAjuizamento="2023-07-25")).registro
    assert r["data_ajuizamento"] is None
    assert r["data_ajuizamento_original"] == "2023-07-25"


def test_assuntos_aninhados_achatados():
    a = norm(hit(assuntos=[{"codigo": 1, "nome": "A"},
                           [{"codigo": 2, "nome": "B"}, {"codigo": 3, "nome": "C"}]])).assuntos
    assert [x["assunto_codigo"] for x in a] == [1, 2, 3]
    assert [x["posicao"] for x in a] == [0, 1, 2]
    assert [x["veio_aninhado"] for x in a] == [False, True, True]


def test_assunto_sem_nome():
    a = norm(hit(assuntos=[{"codigo": 7}])).assuntos
    assert a[0]["assunto_codigo"] == 7 and a[0]["nome_original"] is None


def test_classe_codigo_texto_menos_um():
    assert norm(hit(classe={"codigo": "-1", "nome": "x"})).registro["classe_codigo"] == -1


def test_movimento_sem_orgao_e_orgao_texto():
    ms = norm(hit(movimentos=[
        {"codigo": 1, "nome": "m", "dataHora": "2023-08-01T00:00:00.000Z"},
        {"codigo": 2, "nome": "n", "dataHora": "2023-08-02T00:00:00.000Z",
         "orgaoJulgador": {"codigo": "9099", "nome": "O"}},
        {"codigo": 3, "nome": "o", "dataHora": "2023-08-03T00:00:00.000Z",
         "orgaoJulgador": {"codigo": "abc", "nome": "P"}},
    ])).movimentos
    assert ms[0]["orgao_codigo"] is None and ms[0]["orgao_codigo_original"] is None
    assert ms[1]["orgao_codigo"] == 9099 and ms[1]["orgao_codigo_original"] == "9099"
    assert ms[2]["orgao_codigo"] is None and ms[2]["orgao_codigo_original"] == "abc"


def test_ordem_cronologica_e_dias():
    ms = norm(hit(movimentos=[
        {"codigo": 1, "nome": "tarde", "dataHora": "2023-08-04T10:00:00.000Z"},
        {"codigo": 2, "nome": "cedo", "dataHora": "2023-07-27T10:00:00.000Z"},
    ])).movimentos
    assert [m["ordem_original"] for m in ms] == [0, 1]
    assert [m["ordem_cronologica"] for m in ms] == [1, 0]
    # ajuizamento 2023-07-25 15:41:20; 08-04 10:00 -> 9 dias; 07-27 10:00 -> 1 dia
    assert ms[0]["dias_desde_ajuizamento"] == 9
    assert ms[1]["dias_desde_ajuizamento"] == 1
    assert ms[0]["data_hora"].tzinfo is not None


def test_complementos_preservados():
    ms = norm(hit(movimentos=[{
        "codigo": 1, "nome": "m", "dataHora": "2023-08-01T00:00:00.000Z",
        "complementosTabelados": [
            {"codigo": 10, "descricao": "d1", "valor": 1, "nome": "n1"},
            {"codigo": 11, "descricao": "d2", "valor": 2, "nome": "n2"}]}])).movimentos
    c = ms[0]["complementos"]
    assert [x["ordem"] for x in c] == [0, 1]
    assert c[1] == {"ordem": 1, "codigo": 11, "descricao": "d2", "valor": 2, "nome": "n2"}


def test_identificadores_so_no_bloco_restrito():
    n = norm(hit())
    assert "numero_processo" not in n.registro and "id" not in n.registro
    assert "id_source" not in n.registro
    assert n.identificador["numero_processo"] == "00012345620238160001"
    assert n.identificador["id_source"] == "ID-SINTETICO"
    assert n.identificador["ano_numero_cnj"] == 2023
