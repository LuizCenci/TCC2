-- gold.processo_categoria: categorias por registro selecionado. Sem commit.
TRUNCATE gold.processo_categoria;

INSERT INTO gold.processo_categoria (registro_id, categoria, somente_ampliada)
SELECT ra.registro_id, ac.categoria, bool_and(ac.somente_ampliada)
  FROM gold.fato_processo f
  JOIN silver.registro_assunto ra USING (registro_id)
  JOIN ref.assunto_categoria ac ON ac.assunto_codigo = ra.assunto_codigo
 GROUP BY ra.registro_id, ac.categoria;

INSERT INTO gold.processo_categoria (registro_id, categoria, somente_ampliada)
SELECT f.registro_id, 'VD_SEM_ESPECIFICACAO', false
  FROM gold.fato_processo f
 WHERE NOT EXISTS (SELECT 1 FROM gold.processo_categoria pc WHERE pc.registro_id = f.registro_id)
   AND EXISTS (SELECT 1 FROM silver.registro_assunto ra
                WHERE ra.registro_id = f.registro_id
                  AND ra.assunto_codigo IN (10949, 11979, 10948));

ANALYZE gold.processo_categoria;
