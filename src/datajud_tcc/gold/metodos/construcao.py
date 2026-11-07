"""Construção dos agregados Python da Gold (taxas, tempos, desfechos); sem commit."""

import logging
import time

from datajud_tcc.gold import referencias
from datajud_tcc.gold.metodos import sobrevivencia, taxas

logger = logging.getLogger(__name__)

TABELAS_AGG = (
    "agg_volume", "agg_volume_jan_ago", "agg_categoria", "agg_mpu", "agg_mpu_medida",
    "agg_cautelar", "agg_qualidade_orgao", "agg_cobertura_cnj", "agg_pipeline",
    "agg_taxa", "agg_tempo", "agg_desfecho",
)


def construir_agregados(conn, versao_regras: str) -> dict[str, int]:
    """Roda os passos Python (os SQL 40_* já rodam em construir_gold); devolve linhas por tabela."""
    esperada = referencias.ler_regras()["versao_regras"]
    if versao_regras != esperada:
        raise ValueError(f"versão de regras divergente: {versao_regras!r} != {esperada!r}")
    for nome, fn in (("taxa", taxas.construir_agg_taxa),
                     ("tempo", sobrevivencia.construir_agg_tempo),
                     ("desfecho", sobrevivencia.construir_agg_desfecho)):
        t = time.monotonic()
        fn(conn)
        logger.info("agregados %s concluídos em %.1fs", nome, time.monotonic() - t)
    return {t: conn.execute(f"SELECT count(*) FROM gold.{t}").fetchone()[0] for t in TABELAS_AGG}
