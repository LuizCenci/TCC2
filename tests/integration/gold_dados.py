"""Dados sintéticos mínimos para os testes da Gold (gravam direto na Silver)."""

from datetime import datetime, timezone


def inserir_execucao(conn, run_id, concluida_em, anos, updated_since=None):
    conn.execute(
        "INSERT INTO controle.execucao_coleta (run_id, updated_since, status_coleta, concluida_em)"
        " VALUES (%s, %s, 'concluida', %s)", (run_id, updated_since, concluida_em))
    for ano in anos:
        conn.execute(
            "INSERT INTO controle.pagina_bronze (run_id, ano, pagina, sha256, n_registros)"
            " VALUES (%s, %s, 1, %s, 0)", (run_id, ano, "0" * 64))


def inserir_registro(conn, run_id, api_id, *, ano, classe, orgao, municipio, ajuizamento,
                     assuntos, movimentos=(), numero):
    """movimentos: iterável de (codigo, datetime). Retorna registro_id."""
    movimentos = list(movimentos)
    rid = conn.execute(
        """INSERT INTO silver.registro (run_id, api_id, ano_particao, pagina, classe_codigo,
               orgao_codigo, municipio_sede_ibge, data_ajuizamento, n_movimentos, hash_source)
           VALUES (%s,%s,%s,1,%s,%s,%s,%s,%s,%s) RETURNING registro_id""",
        (run_id, api_id, ano, classe, orgao, municipio, ajuizamento, len(movimentos),
         "0" * 64)).fetchone()[0]
    conn.execute(
        "INSERT INTO restrito.identificador (registro_id, numero_processo, id_source)"
        " VALUES (%s,%s,%s)", (rid, numero, api_id))
    for pos, cod in enumerate(assuntos):
        conn.execute(
            "INSERT INTO silver.registro_assunto (registro_id, posicao, assunto_codigo, veio_aninhado)"
            " VALUES (%s,%s,%s,false)", (rid, pos, cod))
    for i, (cod, dh) in enumerate(movimentos):
        conn.execute(
            """INSERT INTO silver.movimento (movimento_id, registro_id, codigo, data_hora,
                   dias_desde_ajuizamento, ordem_original, ordem_cronologica)
               VALUES (nextval('silver.movimento_id_seq'), %s, %s, %s, %s, %s, %s)""",
            (rid, cod, dh, None if dh is None else (dh.replace(tzinfo=None) - ajuizamento).days,
             i, i))
    return rid


def utc(ano, mes, dia, hora=12):
    return datetime(ano, mes, dia, hora, tzinfo=timezone.utc)
