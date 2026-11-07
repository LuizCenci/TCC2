"""Exportação dos agregados públicos (gold.agg_*) com supressão de células pequenas."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from datajud_tcc.gold import referencias
from datajud_tcc.gold.metodos import supressao

CONTAGENS = {
    "agg_mpu": ("n_com_decisao", "n_deferimento", "n_parcial", "n_indeferimento", "n_revogadas"),
    "agg_cautelar": ("n_flagrante", "n_preventiva", "n_liberdade_provisoria_concedida"),
    "agg_tempo": ("n_eventos",), "agg_desfecho": ("n_desfecho",),
    "agg_qualidade_orgao": ("n_processos_com_duplicado",),
}
# Colapso (só na exportação) sobre mesorregiao_id: (dimensões mantidas, somas)
COLAPSOS = {
    "agg_volume": (("pergunta", "ano_ajuizamento", "ano_parcial", "mes_ajuizamento",
                    "tipo_procedimento", "serie"), ("n",)),
    "agg_mpu": (("pergunta", "ano_ajuizamento", "ano_parcial", "orgao_especializado", "serie"),
                ("n",) + CONTAGENS["agg_mpu"]),
}


def _colapsar(linhas, dims, somas):
    acc: dict[tuple, dict] = {}
    for l in linhas:
        k = tuple(l[d] for d in dims)
        a = acc.setdefault(k, {**{d: l[d] for d in dims}, **{c: None for c in somas}})
        for c in somas:
            if l[c] is not None:
                a[c] = (a[c] or 0) + l[c]
    return list(acc.values())
# tabela: (limite, colunas_grupo, colunas_valor) ou None (sem supressão)
REGRAS: dict[str, tuple[int, tuple[str, ...], tuple[str, ...]] | None] = {
    "agg_volume": (5, ("pergunta", "ano_ajuizamento", "ano_parcial", "tipo_procedimento", "serie"), ()),
    "agg_volume_jan_ago": (5, ("pergunta", "ano_ajuizamento", "tipo_procedimento", "serie"), ()),
    "agg_categoria": (5, ("pergunta", "ano_ajuizamento", "ano_parcial", "tipo_procedimento",
                          "categoria", "serie"), ()),
    "agg_taxa": (5, ("pergunta", "ano_ajuizamento", "ano_parcial", "tipo_procedimento", "serie"),
                 ("taxa_bruta_100k", "taxa_eb_100k")),
    "agg_mpu": (5, ("pergunta", "ano_ajuizamento", "ano_parcial", "serie"),
                ("n_com_decisao", "n_deferimento", "n_parcial", "n_indeferimento", "n_revogadas")),
    "agg_mpu_medida": (5, ("pergunta", "ano_ajuizamento", "ano_parcial", "tipo_medida"), ()),
    "agg_cautelar": (5, ("pergunta", "ano_ajuizamento", "ano_parcial", "tipo_procedimento",
                         "categoria", "serie"),
                     ("n_flagrante", "n_preventiva", "n_liberdade_provisoria_concedida")),
    "agg_tempo": (5, ("pergunta", "marco", "tipo_procedimento", "serie", "estrato"),
                  ("n_eventos", "mediana_dias", "mediana_alcancada", "ic95_inf", "ic95_sup",
                   "pct_evento_ate_2", "pct_evento_ate_30", "pct_evento_ate_365",
                   "pct_evento_ate_730")),
    "agg_desfecho": (5, ("pergunta", "tipo_procedimento", "serie", "variante", "estrato",
                         "desfecho"),
                     ("n_desfecho", "ia_365", "ia_730", "ia_1095", "ia_1825")),
    "agg_qualidade_orgao": (10, ("mesorregiao_id",),
                            ("media_movimentos", "mediana_movimentos",
                             "n_processos_com_duplicado")),
    "agg_cobertura_cnj": None,
    "agg_pipeline": None,
}


def _celula(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, datetime):
        return v.isoformat()
    return str(v)


def exportar(conn, destino: Path = Path("outputs/publicacao")) -> Path:
    corte = conn.execute("SELECT max(data_corte) FROM gold.fato_processo").fetchone()[0]
    corte_s = corte.isoformat() if hasattr(corte, "isoformat") else str(corte)
    linha = conn.execute(
        "SELECT versao_regras FROM controle.execucao_gold ORDER BY construida_em DESC LIMIT 1"
    ).fetchone()
    versao = linha[0] if linha else referencias.ler_regras()["versao_regras"]
    pasta = Path(destino) / f"{corte_s[:10]}_{versao}"
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos = []
    for tabela, regra in REGRAS.items():
        cur = conn.execute(f"SELECT * FROM gold.{tabela}")  # noqa: S608 (nomes fixos)
        cols = [d.name for d in cur.description]
        linhas = [dict(zip(cols, r)) for r in cur.fetchall()]
        if tabela in COLAPSOS:
            dims, somas = COLAPSOS[tabela]
            linhas = _colapsar(linhas, dims, somas)
            cols = list(dims) + list(somas)
        if regra is not None:
            limite, grupo, valor = regra
            linhas = supressao.aplicar(linhas, limite=limite, colunas_grupo=grupo,
                                       colunas_valor=valor,
                                       colunas_contagem=CONTAGENS.get(tabela, ()))
            cols = cols + ["suprimido", "suprimido_parcial"]
        caminho = pasta / f"{tabela}.csv"
        with open(caminho, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for l in linhas:
                w.writerow([_celula(l.get(c)) for c in cols])
        arquivos.append({"arquivo": caminho.name, "linhas": len(linhas),
                         "sha256": hashlib.sha256(caminho.read_bytes()).hexdigest()})
    regras_txt = {t: ({"limite": r[0], "colunas_grupo": list(r[1]), "colunas_valor": list(r[2])}
                      if r else "sem supressão") for t, r in REGRAS.items()}
    manifesto = {"versao_regras": versao, "data_corte_max": corte_s,
                 "gerado_em": datetime.now(timezone.utc).isoformat(),
                 "arquivos": arquivos, "regras_supressao": regras_txt,
                 "subcontagens_suprimidas_abaixo_do_limite": {t: list(c) for t, c in CONTAGENS.items()},
                 "agregacoes_exportacao": {
                     t: "somado sobre mesorregiao_id (coluna removida); nível mesorregional "
                        "disponível em agg_taxa (n) e agg_volume_jan_ago" for t in COLAPSOS},
                 "observacao": "estimavel é mantido (revela apenas n < 30)"}
    (pasta / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    return pasta

