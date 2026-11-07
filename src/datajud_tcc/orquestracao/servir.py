"""Publica os fluxos e mantém o agendamento ativo enquanto o processo rodar.

Uso (na raiz do projeto): python -m datajud_tcc.orquestracao.servir

- coleta incremental semanal, segunda 03:17 (fora da virada da hora, onde os
  HTTP 429 se concentraram — docs/artigo/03-desempenho-api-coleta.md);
- pipeline completo (coleta → Silver → Gold) sob demanda, até a Silver existir.
Uma execução por vez em cada implantação (limit=1).
"""

from __future__ import annotations

from pathlib import Path

from prefect import serve

from ..registro_log import configurar_arquivo

from .fluxos import CATALOGO, coleta_incremental, pipeline_incremental

CONFIG = "config/collection.incremental.yaml"


def main() -> None:
    configurar_arquivo(Path("work/logs/orquestracao.log"),
                       ("datajud_tcc", "prefect.flow_runs", "prefect.task_runs"))
    coleta = coleta_incremental.to_deployment(
        name="tjpr-incremental-semanal",
        cron="17 3 * * 1",
        parameters={"config_path": CONFIG, "catalogo": str(CATALOGO)},
        tags=["datajud", "base-operacional"],
    )
    pipeline = pipeline_incremental.to_deployment(
        name="tjpr-pipeline-sob-demanda",
        parameters={"config_path": CONFIG, "versao_regras": "gold-2026-11-07"},
        tags=["datajud", "base-operacional"],
    )
    serve(coleta, pipeline, limit=1)


if __name__ == "__main__":
    main()
