-- gold.fato_evento: so movimentos de registros selecionados com fase mapeada. Sem commit.
-- orgao_codigo mantem o tipo da Silver (int).
TRUNCATE gold.fato_evento;

INSERT INTO gold.fato_evento (registro_id, seq, dt_evento, dias_desde_ajuizamento,
                              movimento_codigo, fase, subtipo, orgao_codigo)
SELECT m.registro_id, m.ordem_cronologica, m.data_hora, m.dias_desde_ajuizamento,
       m.codigo, mf.fase, NULLIF(mf.subtipo, ''), m.orgao_codigo
  FROM gold.fato_processo f
  JOIN silver.movimento m ON m.registro_id = f.registro_id
  JOIN ref.movimento_fase mf ON mf.movimento_codigo = m.codigo;

ANALYZE gold.fato_evento;
