-- Views de qualidade da Gold. Sem identificadores processuais.
CREATE OR REPLACE VIEW gold.qualidade_volume_mensal AS
SELECT ano_ajuizamento AS ano, mes_ajuizamento AS mes, tipo_procedimento AS tipo,
       count(*) AS n
  FROM gold.fato_processo
 GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW gold.qualidade_intensidade_registro AS
SELECT orgao_codigo, mesorregiao_id, count(*) AS n_processos,
       avg(n_movimentos)::numeric(12,2) AS media_movimentos,
       percentile_cont(0.5) WITHIN GROUP (ORDER BY n_movimentos) AS mediana_movimentos
  FROM gold.fato_processo
 GROUP BY orgao_codigo, mesorregiao_id;

CREATE OR REPLACE VIEW gold.qualidade_movimentos_duplicados AS
WITH dup AS (
    SELECT m.registro_id, m.codigo, m.data_hora
      FROM silver.movimento m
      JOIN gold.fato_processo f USING (registro_id)
     GROUP BY m.registro_id, m.codigo, m.data_hora
    HAVING count(*) > 1
)
SELECT f.orgao_codigo, count(DISTINCT d.registro_id) AS n_processos,
       count(*) AS n_grupos_duplicados
  FROM dup d JOIN gold.fato_processo f USING (registro_id)
 GROUP BY f.orgao_codigo;

CREATE OR REPLACE VIEW gold.qualidade_sem_mapeamento AS
SELECT f.registro_id, f.municipio_sede_ibge, f.classe_codigo,
       (f.mesorregiao_id IS NULL) AS sem_mesorregiao,
       NOT EXISTS (SELECT 1 FROM ref.classe_tipo ct
                    WHERE ct.classe_codigo = f.classe_codigo) AS classe_fora_ref,
       NOT EXISTS (SELECT 1 FROM gold.processo_categoria pc
                    WHERE pc.registro_id = f.registro_id) AS sem_categoria
  FROM gold.fato_processo f
 WHERE f.mesorregiao_id IS NULL
    OR NOT EXISTS (SELECT 1 FROM ref.classe_tipo ct WHERE ct.classe_codigo = f.classe_codigo)
    OR NOT EXISTS (SELECT 1 FROM gold.processo_categoria pc WHERE pc.registro_id = f.registro_id);

CREATE OR REPLACE VIEW gold.qualidade_cobertura_referencias AS
WITH cod AS (
    SELECT DISTINCT m.codigo
      FROM silver.movimento m JOIN gold.fato_processo f USING (registro_id)
)
SELECT
  100.0 * count(*) FILTER (WHERE tipo_procedimento = 'OUTROS') / NULLIF(count(*), 0)
      AS tipo_outros_pct,
  100.0 * count(*) FILTER (WHERE NOT EXISTS (
      SELECT 1 FROM gold.processo_categoria pc WHERE pc.registro_id = f.registro_id))
      / NULLIF(count(*), 0) AS sem_categoria_pct,
  (SELECT 100.0 * count(*) FILTER (WHERE NOT EXISTS (
              SELECT 1 FROM ref.movimento_fase mf WHERE mf.movimento_codigo = cod.codigo))
              / NULLIF(count(*), 0) FROM cod) AS movimentos_sem_fase_pct
  FROM gold.fato_processo f;
