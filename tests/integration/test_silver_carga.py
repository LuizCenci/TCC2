"""Testes da carga transacional de uma execução (dados sintéticos)."""
import gzip
import json

import pytest

from datajud_tcc.bronze import BronzeStore
from datajud_tcc.silver.carga import ExecucaoInvalida, carregar_execucao
from datajud_tcc.silver.esquema import aplicar_esquema

pytestmark = pytest.mark.banco


def _hit(api_id, numero, **extra):
    src = {
        "id": "SRC-" + api_id,
        "numeroProcesso": numero,
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
        "movimentos": [
            {"codigo": 26, "nome": "Distribuição", "dataHora": "2023-07-25T15:41:20.000Z",
             "orgaoJulgador": {"codigo": 5, "nome": "Vara"},
             "complementosTabelados": [
                 {"codigo": 2, "descricao": "d", "valor": 1, "nome": "n"}]},
            {"codigo": 51, "nome": "Sem órgão", "dataHora": "2023-08-01T10:00:00.000Z"},
        ],
    }
    src.update(extra)
    return {"_id": api_id, "_index": "i", "_score": None, "_source": src, "sort": [1]}


def _resposta(hits, total=100):
    return {"took": 1, "timed_out": False,
            "hits": {"total": {"value": total, "relation": "eq"}, "hits": hits}}


def _criar_execucao(raiz, run_id="run-sint", status="complete", anos=(2024, 2026), prefixo="A"):
    store = BronzeStore(raiz)
    particoes = {}
    for ano in anos:
        artefatos = []
        # página 1 com 2 registros (um com assunto aninhado), página 2 com 1
        paginas = [
            [_hit(f"{prefixo}{ano}-1", f"0000001{ano}000000000"),
             _hit(f"{prefixo}{ano}-2", f"0000002{ano}000000000",
                  assuntos=[[{"codigo": 7, "nome": "X"}, {"codigo": 8, "nome": "Y"}]])],
            [_hit(f"{prefixo}{ano}-3", f"0000003{ano}000000000")],
        ]
        for n, hits in enumerate(paginas, start=1):
            art = store.write_page(ano, n, {"q": 1}, _resposta(hits))
            artefatos.append({
                "page": n,
                "request": str(art.request_path.relative_to(raiz)).replace("\\", "/"),
                "response": str(art.response_path.relative_to(raiz)).replace("\\", "/"),
                "sha256": art.sha256, "records": len(hits)})
        particoes[str(ano)] = {
            "artifacts": artefatos,
            "records": sum(a["records"] for a in artefatos),
            "total": {"value": 100, "relation": "eq"}}
    manifesto = {
        "run_id": run_id, "status": status, "catalog_version": "cat-1",
        "catalog_source_hash": "a" * 64, "config_hash": "b" * 64,
        "collector_version": "0.1", "created_at": "2026-11-05T10:00:00Z",
        "finished_at": "2026-11-05T11:00:00Z", "partitions": particoes}
    (raiz / "manifest.json").write_text(json.dumps(manifesto), encoding="utf-8")
    return manifesto


def _conta(conn, run_id):
    return conn.execute(
        "SELECT (SELECT count(*) FROM silver.registro WHERE run_id=%(r)s),"
        " (SELECT count(*) FROM silver.movimento m JOIN silver.registro g USING (registro_id) WHERE g.run_id=%(r)s),"
        " (SELECT count(*) FROM controle.pagina_bronze WHERE run_id=%(r)s)",
        {"r": run_id}).fetchone()


def test_carga_conta_linhas(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path)
    r = carregar_execucao(conn_banco, tmp_path)
    assert r == {"paginas": 4, "registros": 6, "assuntos": 8, "movimentos": 12, "complementos": 6}
    assert _conta(conn_banco, "run-sint") == (6, 12, 4)


def test_carga_e_idempotente(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path)
    r1 = carregar_execucao(conn_banco, tmp_path)
    r2 = carregar_execucao(conn_banco, tmp_path)
    assert r1 == r2
    assert _conta(conn_banco, "run-sint") == (6, 12, 4)


def test_hash_divergente_aborta_sem_gravar(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path)
    alvo = tmp_path / "responses" / "year=2026" / "page=000002.response.json.gz"
    alvo.write_bytes(gzip.compress(b'{"hits":{"hits":[]}}', mtime=0))
    with pytest.raises(ExecucaoInvalida):
        carregar_execucao(conn_banco, tmp_path)
    assert _conta(conn_banco, "run-sint") == (0, 0, 0)
    assert conn_banco.execute(
        "SELECT count(*) FROM controle.execucao_coleta WHERE run_id='run-sint'"
    ).fetchone()[0] == 0


def test_execucao_incompleta_rejeitada(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path, status="running")
    with pytest.raises(ExecucaoInvalida):
        carregar_execucao(conn_banco, tmp_path)


def test_todas_as_particoes_sao_carregadas(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path, anos=(2024, 2026))
    carregar_execucao(conn_banco, tmp_path)
    anos = {a for (a,) in conn_banco.execute(
        "SELECT DISTINCT ano_particao FROM silver.registro WHERE run_id='run-sint'")}
    assert anos == {2024, 2026}


def test_mesmo_api_id_em_duas_execucoes_convive(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(); b.mkdir()
    _criar_execucao(a, run_id="run-a", anos=(2024,))
    _criar_execucao(b, run_id="run-b", anos=(2024,))
    carregar_execucao(conn_banco, a)
    carregar_execucao(conn_banco, b)
    n = conn_banco.execute(
        "SELECT count(*) FROM silver.registro WHERE api_id='A2024-1'").fetchone()[0]
    assert n == 2


def test_identificador_fica_em_restrito(conn_banco, tmp_path):
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path, anos=(2024,))
    carregar_execucao(conn_banco, tmp_path)
    cols = {c for (c,) in conn_banco.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_schema='silver' AND table_name='registro'")}
    assert not any("numero" in c for c in cols)
    numeros = {n for (n,) in conn_banco.execute(
        "SELECT i.numero_processo FROM restrito.identificador i "
        "JOIN silver.registro g USING (registro_id) WHERE g.run_id='run-sint'")}
    assert "00000012024000000000" in numeros


def test_carga_usa_copy_para_movimentos(conn_banco, tmp_path, monkeypatch):
    import psycopg
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path, anos=(2024,))
    chamadas = []
    original = psycopg.Cursor.copy

    def espiao(self, statement, *args, **kwargs):
        chamadas.append(str(statement))
        return original(self, statement, *args, **kwargs)

    monkeypatch.setattr(psycopg.Cursor, "copy", espiao)
    carregar_execucao(conn_banco, tmp_path)
    assert any("silver.movimento" in c for c in chamadas)


def test_carga_registra_progresso_por_pagina(conn_banco, caplog, tmp_path):
    import logging
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path, anos=(2024,))
    with caplog.at_level(logging.INFO, logger="datajud_tcc.silver.carga"):
        carregar_execucao(conn_banco, tmp_path)
    texto = caplog.text
    assert "1/2 páginas" in texto and "2/2 páginas" in texto
    assert "registros=3" in texto and "duração=" in texto
    assert "0000001" not in texto and "postgresql://" not in texto


def test_carga_ja_carregada_registra_que_nada_foi_gravado(conn_banco, caplog, tmp_path):
    import logging
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path)
    carregar_execucao(conn_banco, tmp_path)
    caplog.clear()
    with caplog.at_level(logging.INFO, logger="datajud_tcc.silver.carga"):
        carregar_execucao(conn_banco, tmp_path)
    assert "nada foi gravado" in caplog.text


def test_contagem_de_movimentos_divergente_aborta(conn_banco, tmp_path, monkeypatch):
    import dataclasses
    from datajud_tcc.silver import carga
    aplicar_esquema(conn_banco)
    _criar_execucao(tmp_path, anos=(2024,))
    original = carga.normalizar_hit

    def sem_um_movimento(*args, **kwargs):
        n = original(*args, **kwargs)
        return dataclasses.replace(n, movimentos=n.movimentos[:-1])  # n_movimentos permanece

    monkeypatch.setattr(carga, "normalizar_hit", sem_um_movimento)
    with pytest.raises(ExecucaoInvalida):
        carregar_execucao(conn_banco, tmp_path)
    conn_banco.rollback()
    assert _conta(conn_banco, "run-sint") == (0, 0, 0)
