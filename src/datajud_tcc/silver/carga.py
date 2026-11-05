"""Carga transacional de uma execução da Bronze na Silver (sem commit)."""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path

from datajud_tcc.silver.normalizacao import normalizar_hit


class ExecucaoInvalida(ValueError):
    """Execução da Bronze incompleta, inconsistente ou com página adulterada."""


_COLS_MOV = (
    "movimento_id", "registro_id", "codigo", "nome_original", "data_hora",
    "dias_desde_ajuizamento", "orgao_codigo_original", "orgao_codigo", "orgao_nome",
    "ordem_original", "ordem_cronologica",
)
_COLS_COMP = ("movimento_id", "ordem", "codigo", "descricao", "valor", "nome")


def _contagens(conn, run_id: str) -> dict[str, int]:
    linha = conn.execute(
        "SELECT"
        " (SELECT count(*) FROM controle.pagina_bronze WHERE run_id = %(r)s),"
        " (SELECT count(*) FROM silver.registro WHERE run_id = %(r)s),"
        " (SELECT count(*) FROM silver.registro_assunto a JOIN silver.registro g USING (registro_id)"
        "   WHERE g.run_id = %(r)s),"
        " (SELECT count(*) FROM silver.movimento m JOIN silver.registro g USING (registro_id)"
        "   WHERE g.run_id = %(r)s),"
        " (SELECT count(*) FROM silver.complemento_movimento c"
        "   JOIN silver.movimento m USING (movimento_id)"
        "   JOIN silver.registro g USING (registro_id) WHERE g.run_id = %(r)s)",
        {"r": run_id},
    ).fetchone()
    chaves = ("paginas", "registros", "assuntos", "movimentos", "complementos")
    return dict(zip(chaves, (int(x) for x in linha)))


def _paginas_do_manifesto(manifesto: dict, raiz: Path) -> list[tuple[int, dict, Path]]:
    paginas = []
    for ano_txt, particao in sorted(manifesto.get("partitions", {}).items()):
        for art in sorted(particao.get("artifacts", []), key=lambda a: a["page"]):
            paginas.append((int(ano_txt), art, raiz / art["response"]))
    return paginas


def _verificar_hashes(paginas) -> None:
    for ano, art, caminho in paginas:
        if not caminho.is_file():
            raise ExecucaoInvalida(f"página ausente: ano {ano}, página {art['page']}")
        if hashlib.sha256(caminho.read_bytes()).hexdigest() != art["sha256"]:
            raise ExecucaoInvalida(f"SHA-256 divergente: ano {ano}, página {art['page']}")


def carregar_execucao(conn, run_root: Path) -> dict[str, int]:
    """Carrega todas as partições de uma execução completa. Não faz commit."""
    raiz = Path(run_root)
    try:
        manifesto = json.loads((raiz / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as erro:
        raise ExecucaoInvalida("manifesto ilegível") from erro
    if manifesto.get("status") != "complete":
        raise ExecucaoInvalida("execução não está completa")
    run_id = manifesto["run_id"]
    paginas = _paginas_do_manifesto(manifesto, raiz)
    _verificar_hashes(paginas)

    if conn.execute(
        "SELECT 1 FROM controle.execucao_coleta WHERE run_id = %s", (run_id,)
    ).fetchone():
        return _contagens(conn, run_id)

    conn.execute(
        "INSERT INTO controle.execucao_coleta (run_id, catalogo_versao, catalogo_sha256,"
        " config_hash, versao_coletor, updated_since, status_coleta, criada_em, concluida_em)"
        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (run_id, manifesto.get("catalog_version"), manifesto.get("catalog_source_hash"),
         manifesto.get("config_hash"), manifesto.get("collector_version"),
         manifesto.get("updated_since"), manifesto.get("status"),
         manifesto.get("created_at"), manifesto.get("finished_at")),
    )

    esperado = 0
    for ano, art, caminho in paginas:
        esperado += art["records"]
        with gzip.open(caminho, "rb") as arq:
            resposta = json.loads(arq.read().decode("utf-8"))
        hits = (resposta.get("hits") or {}).get("hits") or []
        total = ((manifesto["partitions"][str(ano)].get("total")) or {}).get("value")
        conn.execute(
            "INSERT INTO controle.pagina_bronze (run_id, ano, pagina, sha256, n_registros, total_api)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (run_id, ano, art["page"], art["sha256"], len(hits), total),
        )
        _carregar_pagina(conn, hits, run_id, ano, art["page"])

    if _contagens(conn, run_id)["registros"] != esperado:
        raise ExecucaoInvalida("contagem de registros difere do manifesto")
    return _contagens(conn, run_id)


def _carregar_pagina(conn, hits: list, run_id: str, ano: int, pagina: int) -> None:
    normalizados = [normalizar_hit(h, run_id=run_id, ano=ano, pagina=pagina) for h in hits]
    if not normalizados:
        return
    cols = list(normalizados[0].registro)
    sql = (f"INSERT INTO silver.registro ({', '.join(cols)}) "
           f"VALUES ({', '.join('%s' for _ in cols)}) RETURNING registro_id")
    ids = []
    with conn.cursor() as cur:
        for n in normalizados:
            ids.append(cur.execute(sql, [n.registro[c] for c in cols]).fetchone()[0])
        cur.executemany(
            "INSERT INTO restrito.identificador (registro_id, numero_processo, id_source,"
            " ano_numero_cnj) VALUES (%s, %s, %s, %s)",
            [(rid, n.identificador["numero_processo"], n.identificador["id_source"],
              n.identificador["ano_numero_cnj"]) for rid, n in zip(ids, normalizados)],
        )
        cur.executemany(
            "INSERT INTO silver.registro_assunto (registro_id, posicao, assunto_codigo,"
            " nome_original, veio_aninhado) VALUES (%s, %s, %s, %s, %s)",
            [(rid, a["posicao"], a["assunto_codigo"], a["nome_original"], a["veio_aninhado"])
             for rid, n in zip(ids, normalizados) for a in n.assuntos],
        )
        movs = [(rid, m) for rid, n in zip(ids, normalizados) for m in n.movimentos]
        if not movs:
            return
        mids = [r[0] for r in cur.execute(
            "SELECT nextval('silver.movimento_id_seq') FROM generate_series(1, %s)",
            (len(movs),)).fetchall()]
        with cur.copy(f"COPY silver.movimento ({', '.join(_COLS_MOV)}) FROM STDIN") as copia:
            for mid, (rid, m) in zip(mids, movs):
                copia.write_row((mid, rid) + tuple(m[c] for c in _COLS_MOV[2:]))
        comps = [(mid,) + tuple(c[k] for k in _COLS_COMP[1:])
                 for mid, (_, m) in zip(mids, movs) for c in m["complementos"]]
        if comps:
            with cur.copy(
                f"COPY silver.complemento_movimento ({', '.join(_COLS_COMP)}) FROM STDIN"
            ) as copia:
                for linha in comps:
                    copia.write_row(linha)
