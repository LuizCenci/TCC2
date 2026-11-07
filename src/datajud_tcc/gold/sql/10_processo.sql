-- gold.fato_processo: versão mais recente por api_id (maior concluida_em,
-- desempate pelo maior run_id), classificação e território. Sem commit.
TRUNCATE gold.fato_processo;

INSERT INTO gold.fato_processo (
    registro_id, run_id, data_corte, ano_particao, classe_codigo, tipo_procedimento, juri,
    orgao_codigo, orgao_especializado, municipio_sede_ibge, mesorregiao_id,
    data_ajuizamento, ano_ajuizamento, mes_ajuizamento, serie_estrita,
    feminicidio_tentado, infracional, n_movimentos, numero_repetido,
    removido_indice, data_ajuizamento_nula)
WITH sel AS (
    SELECT DISTINCT ON (r.api_id)
           r.registro_id, r.run_id, r.api_id, r.ano_particao, r.classe_codigo,
           r.orgao_codigo, r.municipio_sede_ibge, r.data_ajuizamento, r.n_movimentos,
           e.concluida_em, e.catalogo_sha256
      FROM silver.registro r
      JOIN controle.execucao_coleta e USING (run_id)
     ORDER BY r.api_id, e.concluida_em DESC NULLS LAST, r.run_id DESC
),
num AS (
    SELECT s.registro_id,
           (i.numero_processo IS NOT NULL
            AND count(*) OVER (PARTITION BY i.numero_processo) > 1) AS repetido
      FROM sel s
      LEFT JOIN restrito.identificador i USING (registro_id)
),
cat AS (
    SELECT ra.registro_id,
           bool_or(c.grupo IN ('nucleo_pvd', 'especifica')) AS estrita_assunto,
           bool_and(c.natureza = 'infracional') AS so_infracional
      FROM silver.registro_assunto ra
      JOIN ref.catalogo c ON c.tipo = 'assunto' AND c.codigo = ra.assunto_codigo
     GROUP BY ra.registro_id
),
ass AS (
    SELECT ra.registro_id,
           bool_or(ra.assunto_codigo = 12091) AS tem_12091,
           bool_or(ra.assunto_codigo = 5555) AS tem_5555,
           bool_or(COALESCE(ac.infracional, false)) AS infrac_categoria
      FROM silver.registro_assunto ra
      LEFT JOIN ref.assunto_categoria ac USING (assunto_codigo)
     GROUP BY ra.registro_id
)
SELECT s.registro_id, s.run_id, (s.concluida_em AT TIME ZONE 'UTC')::date, s.ano_particao, s.classe_codigo,
       COALESCE(ct.tipo_procedimento, 'OUTROS'), COALESCE(ct.juri, false),
       s.orgao_codigo,
       EXISTS (SELECT 1 FROM ref.orgao_especializado oe WHERE oe.orgao_codigo = s.orgao_codigo),
       s.municipio_sede_ibge, m.mesorregiao_id,
       s.data_ajuizamento,
       EXTRACT(YEAR FROM s.data_ajuizamento)::int,
       EXTRACT(MONTH FROM s.data_ajuizamento)::int,
       COALESCE(cat.estrita_assunto, false)
         OR EXISTS (SELECT 1 FROM ref.catalogo cc
                     WHERE cc.tipo = 'classe' AND cc.grupo = 'especifica'
                       AND cc.codigo = s.classe_codigo),
       COALESCE(ass.tem_12091, false) AND COALESCE(ass.tem_5555, false),
       COALESCE(ass.infrac_categoria, false) OR COALESCE(cat.so_infracional, false),
       s.n_movimentos,
       num.repetido,
       EXISTS (
           SELECT 1
             FROM controle.execucao_coleta f
            WHERE f.updated_since IS NULL
              AND f.catalogo_sha256 IS NOT DISTINCT FROM s.catalogo_sha256
              AND f.concluida_em > s.concluida_em
              AND EXISTS (SELECT 1 FROM controle.pagina_bronze p
                           WHERE p.run_id = f.run_id AND p.ano = s.ano_particao)
              AND NOT EXISTS (SELECT 1 FROM silver.registro x
                               WHERE x.run_id = f.run_id AND x.api_id = s.api_id)
       ),
       s.data_ajuizamento IS NULL
  FROM sel s
  JOIN num USING (registro_id)
  LEFT JOIN cat USING (registro_id)
  LEFT JOIN ass USING (registro_id)
  LEFT JOIN ref.classe_tipo ct ON ct.classe_codigo = s.classe_codigo
  LEFT JOIN ref.municipio m ON m.municipio_ibge = s.municipio_sede_ibge;

ANALYZE gold.fato_processo;
