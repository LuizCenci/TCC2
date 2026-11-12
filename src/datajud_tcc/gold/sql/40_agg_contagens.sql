-- Agregados de contagem da Gold (Q01, Q03, Q04/Q07, Q06, Q13, Q14, Q15). Sem identificadores.
-- Cada tabela é truncada e reconstruída aqui. Sem commit.
TRUNCATE gold.agg_volume, gold.agg_volume_jan_ago, gold.agg_categoria, gold.agg_mpu,
         gold.agg_mpu_medida, gold.agg_cautelar, gold.agg_qualidade_orgao,
         gold.agg_cobertura_cnj, gold.agg_pipeline;

CREATE TEMP TABLE IF NOT EXISTS _serie (serie text);
TRUNCATE _serie;
INSERT INTO _serie VALUES ('estrita'), ('ampliada');

INSERT INTO gold.agg_volume
SELECT 'Q01', f.ano_ajuizamento, f.ano_ajuizamento = 2026, f.mes_ajuizamento,
       f.tipo_procedimento, f.mesorregiao_id, s.serie, count(*)
  FROM gold.fato_processo f JOIN _serie s ON s.serie = 'ampliada' OR f.serie_estrita
 GROUP BY 2, 3, 4, 5, 6, 7;

INSERT INTO gold.agg_volume_jan_ago
SELECT 'Q01', f.ano_ajuizamento, f.tipo_procedimento, f.mesorregiao_id, s.serie, count(*)
  FROM gold.fato_processo f JOIN _serie s ON s.serie = 'ampliada' OR f.serie_estrita
 WHERE f.mes_ajuizamento BETWEEN 1 AND 8
 GROUP BY 2, 3, 4, 5;

INSERT INTO gold.agg_categoria
SELECT 'Q03', f.ano_ajuizamento, f.ano_ajuizamento = 2026, f.tipo_procedimento,
       f.mesorregiao_id, pc.categoria, s.serie, count(*)
  FROM gold.fato_processo f
  JOIN gold.processo_categoria pc USING (registro_id)
  JOIN _serie s ON s.serie = 'ampliada' OR (f.serie_estrita AND NOT pc.somente_ampliada)
 GROUP BY 2, 3, 4, 5, 6, 7;

INSERT INTO gold.agg_mpu
SELECT 'Q04', f.ano_ajuizamento, f.ano_ajuizamento = 2026, f.mesorregiao_id,
       f.orgao_especializado, s.serie, count(*),
       count(*) FILTER (WHERE f.resultado_mpu IS NOT NULL),
       count(*) FILTER (WHERE f.resultado_mpu = 'DEFERIMENTO'),
       count(*) FILTER (WHERE f.resultado_mpu = 'PARCIAL'),
       count(*) FILTER (WHERE f.resultado_mpu = 'INDEFERIMENTO'),
       count(*) FILTER (WHERE f.dt_revogacao_mpu IS NOT NULL)
  FROM gold.fato_processo f JOIN _serie s ON s.serie = 'ampliada' OR f.serie_estrita
 WHERE f.tipo_procedimento = 'MPU'
 GROUP BY 2, 3, 4, 5, 6;

INSERT INTO gold.agg_mpu_medida
SELECT 'Q06', f.ano_ajuizamento, f.ano_ajuizamento = 2026, f.mesorregiao_id, c.nome, count(*)
  FROM gold.fato_processo f
  JOIN silver.movimento m USING (registro_id)
  JOIN silver.complemento_movimento c ON c.movimento_id = m.movimento_id
 WHERE m.codigo IN (11423, 11424) AND c.descricao = 'tipo_de_medida_protetiva'
 GROUP BY 2, 3, 4, 5;

WITH ev AS (
    SELECT registro_id,
           bool_or(movimento_codigo = 175) AS flag,
           bool_or(movimento_codigo IN (12140, 15032)) AS prev,
           bool_or(movimento_codigo = 818) AS lp
      FROM gold.fato_evento GROUP BY registro_id
), base AS (
    SELECT f.registro_id, f.ano_ajuizamento, f.tipo_procedimento, f.serie_estrita,
           pc.categoria, pc.somente_ampliada,
           COALESCE(ev.flag, false) AS flag, COALESCE(ev.prev, false) AS prev,
           COALESCE(ev.lp, false) AS lp
      FROM gold.fato_processo f
      JOIN gold.processo_categoria pc USING (registro_id)
      LEFT JOIN ev USING (registro_id)
)
INSERT INTO gold.agg_cautelar
SELECT 'Q13', b.ano_ajuizamento, b.ano_ajuizamento = 2026, b.tipo_procedimento, b.categoria,
       s.serie, count(*), count(*) FILTER (WHERE b.flag), count(*) FILTER (WHERE b.prev),
       count(*) FILTER (WHERE b.lp)
  FROM base b JOIN _serie s ON s.serie = 'ampliada' OR (b.serie_estrita AND NOT b.somente_ampliada)
 GROUP BY 2, 3, 4, 5, 6;

INSERT INTO gold.agg_qualidade_orgao
SELECT 'Q14', i.orgao_codigo, i.mesorregiao_id,
       COALESCE((SELECT bool_or(f.orgao_especializado) FROM gold.fato_processo f
                  WHERE f.orgao_codigo = i.orgao_codigo), false),
       i.n_processos, i.media_movimentos, i.mediana_movimentos,
       COALESCE(d.n_processos, 0)
  FROM gold.qualidade_intensidade_registro i
  LEFT JOIN gold.qualidade_movimentos_duplicados d USING (orgao_codigo);

-- Critérios do painel do CNJ (lidos em 11/11/2026): feminicídio = assunto 12091/12358 com classe
-- de ação penal, execução penal, inquérito ou ato infracional; violência doméstica = assuntos do
-- núcleo ou classes de MPU, excluídos os processos de feminicídio e as cartas.
INSERT INTO gold.agg_cobertura_cnj
WITH cls AS (
    SELECT f.ano_ajuizamento AS ano, f.tipo_procedimento,
           (EXISTS (SELECT 1 FROM silver.registro_assunto a WHERE a.registro_id = f.registro_id
                    AND a.assunto_codigo IN (12091, 12358))
           AND COALESCE(f.classe_codigo IN (282, 283, 1033, 1317, 10943, 10944, 11037, 11528,
                                   386, 1714, 11399, 12727, 12728, 12729, 14696, 279, 1464), false)) AS fem,
           (EXISTS (SELECT 1 FROM silver.registro_assunto a WHERE a.registro_id = f.registro_id
                     AND a.assunto_codigo IN (10948, 10949, 11979, 12194, 12196, 14226, 14227,
                                              14228, 14229, 14942, 14943, 14944, 14945, 14097, 14098))
            OR f.classe_codigo IN (1268, 12423, 15309)) AS vd_cand
      FROM gold.fato_processo f
), cont AS (
    SELECT ano,
           count(*) FILTER (WHERE vd_cand AND NOT fem AND tipo_procedimento <> 'CARTA') AS vd,
           count(*) FILTER (WHERE fem) AS fem
      FROM cls GROUP BY ano
)
SELECT 'Q14', r.ano, r.ano = 2026, x.medida, x.n_base, x.n_cnj,
       100.0 * x.n_base / NULLIF(x.n_cnj, 0), x.n_base
  FROM ref.cnj_casos_novos r
  LEFT JOIN cont c ON c.ano = r.ano
  CROSS JOIN LATERAL (VALUES
    ('vd_criterio_cnj', COALESCE(c.vd, 0), r.vd_novos),
    ('feminicidio_criterio_cnj', COALESCE(c.fem, 0), r.feminicidio_novos)
  ) x (medida, n_base, n_cnj)
 WHERE r.ano >= 2020;

INSERT INTO gold.agg_pipeline (pergunta, run_id, concluida_em, updated_since, carregada_em, n)
SELECT 'Q15', e.run_id, e.concluida_em, e.updated_since, e.carregada_em,
       (SELECT count(*) FROM silver.registro r WHERE r.run_id = e.run_id)
  FROM controle.execucao_coleta e;

INSERT INTO gold.agg_pipeline (pergunta, versao_regras, construida_em, n)
SELECT 'Q15', versao_regras, construida_em, (SELECT count(*) FROM gold.fato_processo)
  FROM controle.execucao_gold ORDER BY construida_em DESC LIMIT 1;

ANALYZE gold.agg_volume;
ANALYZE gold.agg_volume_jan_ago;
ANALYZE gold.agg_categoria;
ANALYZE gold.agg_mpu;
ANALYZE gold.agg_mpu_medida;
ANALYZE gold.agg_cautelar;
ANALYZE gold.agg_qualidade_orgao;
ANALYZE gold.agg_cobertura_cnj;
ANALYZE gold.agg_pipeline;
DROP TABLE _serie;
