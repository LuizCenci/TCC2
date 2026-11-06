# Carga inicial da Silver

Data: 06/11/2026. Status: **verificado** (execução real, contagens consultadas no banco).

## 1. O que foi carregado

Execuções da Bronze que compõem a base de análise 2019–2026 (`13-recoleta-2026.md` §6), carregadas com `datajud-tcc silver-carregar --run-root ...` no PostgreSQL 16 local (`tcc_datajud`). A recoleta de 2026, menor, foi carregada primeiro para medir o tempo real. O PC foi mantido acordado com `scripts/manter_acordado.ps1` durante a carga.

| Execução | Páginas | Registros | Assuntos | Movimentos | Complementos | Duração |
|---|---|---|---|---|---|---|
| `bronze2026-20261105-b67187c` | 73 | 14.507 | 23.695 | 679.894 | 354.896 | 14,4 s |
| `bronze-20261018-9852486` | 721 | 143.337 | 262.823 | 12.994.446 | 6.533.614 | 542,6 s (≈9 min) |
| **Total** | 794 | **157.844** | 286.518 | **13.674.340** | 6.888.510 | ≈9,5 min |

Na execução grande, a verificação de SHA-256 das 721 páginas levou 3,9 s. Em cada execução, a carga conferiu o número de registros com o manifesto e o número de movimentos com a soma de `n_movimentos`. As duas conferências passaram.

A estimativa prévia era de 20 a 40 minutos para ~15 milhões de movimentos. O tempo real foi de ≈9,5 minutos para 13,7 milhões.

## 2. Verificações no banco

- `silver.registro`: 157.844 linhas e **147.020 `api_id` distintos**. A diferença de 10.824 corresponde aos registros de 2026 presentes nas duas execuções.
- Os 147.020 distintos equivalem aos 147.002 da base de análise mais os 18 registros de 2026 que saíram do índice entre 18/10 e 05/11 (`13-recoleta-2026.md`). A Silver guarda os dois, e a Gold escolhe a versão de cada registro.
- Por partição (`ano_particao`):

| 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| 24.956 | 24.766 | 15.120 | 14.492 | 16.023 | 17.631 | 19.507 | 25.349 |

  O total de 2026 soma 10.842 registros da coleta de 18/10 e 14.507 da recoleta.
- Os 157.844 registros têm `data_ajuizamento` preenchida e sua linha em `restrito.identificador`.
- Tamanho do banco: 3.638 MB. Os maiores objetos são `silver.movimento` (2.697 MB) e `silver.complemento_movimento` (789 MB), já com os índices.

## 3. Marca d'água inicial do orquestrador

`datajud-tcc silver-marca-dagua` → **`2026-10-05T18:00:31.594Z`**: a maior `dataHoraUltimaAtualizacao` da Silver. É o valor de `marca_inicial` na primeira execução da coleta incremental (`15-orquestracao-prefect.md` §7). A coleta incremental busca registros com atualização posterior a essa data. Como a marca está um mês antes da recoleta, isso reflete o atraso de indexação do índice público.

## 4. Logs

O detalhe por página, com registros, movimentos e segundos, ficou em `work/logs/silver.log` (não versionado). Fora de um flow do Prefect, a carga foi rodada com `PREFECT_LOGGING_TO_API_WHEN_MISSING_FLOW=ignore`, para evitar o aviso do Prefect sobre logs sem flow run.
