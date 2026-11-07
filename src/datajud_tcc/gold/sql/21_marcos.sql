-- Marcos, desfecho e censura em gold.fato_processo. Sem commit.
-- Eventos validos: data_hora nao nula e dias_desde_ajuizamento >= 0 (data em UTC, como a Silver).
WITH ev AS (
    SELECT registro_id, seq, fase, subtipo,
           (dt_evento AT TIME ZONE 'UTC')::date AS d, dt_evento
      FROM gold.fato_evento
     WHERE dt_evento IS NOT NULL AND dias_desde_ajuizamento >= 0
),
marco AS (
    SELECT registro_id,
           min(d) FILTER (WHERE fase = 'DISTRIBUICAO') AS dt_distribuicao,
           min(d) FILTER (WHERE fase = 'DECISAO_MPU') AS dt_decisao_mpu,
           min(d) FILTER (WHERE fase = 'MPU_REVOGACAO') AS dt_revogacao_mpu,
           min(d) FILTER (WHERE fase = 'RECEBIMENTO_DENUNCIA') AS dt_recebimento_denuncia,
           min(d) FILTER (WHERE fase = 'AUDIENCIA') AS dt_primeira_audiencia,
           min(d) FILTER (WHERE fase IN ('SENTENCA_CONDENATORIA','SENTENCA_ABSOLUTORIA',
               'EXTINCAO_PUNIBILIDADE','PRESCRICAO','SENTENCA_OUTRA')) AS dt_sentenca,
           min(d) FILTER (WHERE fase = 'TRANSITO_JULGADO') AS dt_transito,
           min(d) FILTER (WHERE fase = 'ARQUIVAMENTO' AND subtipo = 'DEFINITIVO') AS dt_arquivamento
      FROM ev GROUP BY registro_id
),
mpu AS (
    SELECT DISTINCT ON (registro_id) registro_id, subtipo
      FROM ev WHERE fase = 'DECISAO_MPU'
     ORDER BY registro_id, dt_evento, seq
),
des AS (
    SELECT DISTINCT ON (registro_id) registro_id,
           CASE fase WHEN 'SENTENCA_CONDENATORIA' THEN 'CONDENACAO'
                     WHEN 'SENTENCA_ABSOLUTORIA' THEN 'ABSOLVICAO'
                     WHEN 'SENTENCA_OUTRA' THEN 'SEM_MERITO'
                     ELSE fase END AS desfecho,
           CASE WHEN fase = 'SENTENCA_CONDENATORIA' THEN subtipo END AS subtipo,
           d
      FROM ev
     WHERE fase IN ('SENTENCA_CONDENATORIA','SENTENCA_ABSOLUTORIA','EXTINCAO_PUNIBILIDADE',
                    'PRESCRICAO','SENTENCA_OUTRA','REJEICAO_DENUNCIA','ARQUIVAMENTO_INVESTIGACAO')
     ORDER BY registro_id, dt_evento, seq
),
rea AS (
    SELECT DISTINCT e.registro_id
      FROM ev e JOIN marco m USING (registro_id)
     WHERE e.fase = 'REATIVACAO' AND e.d > m.dt_arquivamento
),
flag AS (
    SELECT DISTINCT registro_id FROM gold.fato_evento
     WHERE dt_evento IS NULL OR dias_desde_ajuizamento < 0
),
calc AS (
    SELECT f.registro_id, m.dt_distribuicao, m.dt_decisao_mpu, m.dt_revogacao_mpu,
           m.dt_recebimento_denuncia, m.dt_primeira_audiencia, m.dt_sentenca,
           m.dt_transito, m.dt_arquivamento, mpu.subtipo AS resultado_mpu,
           CASE WHEN d.desfecho IS NOT NULL THEN d.desfecho
                WHEN m.dt_arquivamento IS NOT NULL THEN 'ENCERRADO_SEM_DESFECHO'
                ELSE 'EM_ANDAMENTO' END AS desfecho,
           d.subtipo AS desfecho_subtipo,
           CASE WHEN d.desfecho IS NOT NULL THEN d.d
                WHEN m.dt_arquivamento IS NOT NULL THEN m.dt_arquivamento END AS dt_desfecho,
           (rea.registro_id IS NOT NULL) AS reativado,
           (flag.registro_id IS NOT NULL) AS antes
      FROM gold.fato_processo f
      LEFT JOIN marco m ON m.registro_id = f.registro_id
      LEFT JOIN mpu ON mpu.registro_id = f.registro_id
      LEFT JOIN des d ON d.registro_id = f.registro_id
      LEFT JOIN rea ON rea.registro_id = f.registro_id
      LEFT JOIN flag ON flag.registro_id = f.registro_id
)
UPDATE gold.fato_processo f SET
    dt_distribuicao = c.dt_distribuicao, dt_decisao_mpu = c.dt_decisao_mpu,
    dt_revogacao_mpu = c.dt_revogacao_mpu, dt_recebimento_denuncia = c.dt_recebimento_denuncia,
    dt_primeira_audiencia = c.dt_primeira_audiencia, dt_sentenca = c.dt_sentenca,
    dt_transito = c.dt_transito, dt_arquivamento = c.dt_arquivamento,
    resultado_mpu = c.resultado_mpu, desfecho = c.desfecho,
    desfecho_subtipo = c.desfecho_subtipo, dt_desfecho = c.dt_desfecho,
    duracao_dias = CASE WHEN f.data_ajuizamento IS NULL THEN NULL
                        ELSE COALESCE(c.dt_desfecho, f.data_corte) - f.data_ajuizamento::date END,
    censurado = (c.desfecho = 'EM_ANDAMENTO'),
    reativado = c.reativado, evento_antes_ajuizamento = c.antes
  FROM calc c WHERE c.registro_id = f.registro_id;
