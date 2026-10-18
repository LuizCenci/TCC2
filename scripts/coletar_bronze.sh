#!/usr/bin/env bash
# Executa a coleta Bronze definitiva com retomada automática limitada.
# Uso (na raiz do projeto): bash scripts/coletar_bronze.sh <run_id>
# Documentado em docs/artigo/03-desempenho-api-coleta.md, §5.
set -u
RUN_ID="${1:?informe o run_id}"
MAX_RETOMADAS=5
PAUSA_SEGUNDOS=120
LOG="work/logs/${RUN_ID}.log"
mkdir -p work/logs
for tentativa in $(seq 0 "$MAX_RETOMADAS"); do
  echo "$(date +%H:%M:%S) WRAPPER execução ${tentativa}/${MAX_RETOMADAS} do run_id ${RUN_ID}" >> "$LOG"
  .venv/Scripts/datajud-tcc.exe collect --config config/collection.bronze.yaml --run-id "$RUN_ID" >> "$LOG" 2>&1
  codigo=$?
  echo "$(date +%H:%M:%S) WRAPPER saída=${codigo}" >> "$LOG"
  [ "$codigo" -eq 0 ] && exit 0
  [ "$tentativa" -lt "$MAX_RETOMADAS" ] && sleep "$PAUSA_SEGUNDOS"
done
echo "$(date +%H:%M:%S) WRAPPER desistiu após ${MAX_RETOMADAS} retomadas" >> "$LOG"
exit 1
