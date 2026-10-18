# Resultado da coleta Bronze — TJPR, G1, 2019–2026

Status: **verificado** (18/10/2026). Esta é a execução usada na pesquisa.

## 1. Identificação

| Item | Valor |
|---|---|
| `run_id` | `bronze-20261018-9852486` |
| Commit do código | `9852486` |
| Início / fim | 18/10/2026 01:23:32 / 07:19:21 (horário local); `finished_at` = 2026-10-18T10:19:21Z |
| Duração | cerca de 5 h 56 min |
| Catálogo | `tjpr-vcm-2026-10-18`, SHA-256 `df83d3abad719b373da7b97b0e917432dcb1c5a292447d8519c69fef2f245035` |
| Hash da configuração (`config_hash`, impressão digital interna do coletor) | `e0041ebc26ddb9de21d36a8c7fe9e00380ab8207e9af0932f29c0fb12b3942f0` |
| Parâmetros | `01-parametros-da-extracao.md` (v1.2) |
| Armazenamento | `work/bronze/datajud/tjpr/collected_at=2026-10-18/run_id=bronze-20261018-9852486/` (192 MB, 721 páginas), não versionado |
| Status do manifesto | `complete` |

## 2. Completude por ano

Verificação independente da execução: o script `evidencias/scripts/verificar_bronze.py` relê todas as páginas gravadas, sem depender dos contadores do coletor.

| Ano | Páginas | Registros coletados | Total informado pela API (`eq`) | IDs únicos | Datas fora do ano | Na análise? |
|---|---:|---:|---:|---:|---:|---|
| 2019 | 125 | 24.956 | 24.956 | 24.956 | 0 | sim |
| 2020 | 124 | 24.766 | 24.766 | 24.766 | 0 | sim |
| 2021 | 76 | 15.120 | 15.120 | 15.120 | 0 | sim |
| 2022 | 73 | 14.492 | 14.492 | 14.492 | 0 | sim |
| 2023 | 81 | 16.023 | 16.023 | 16.023 | 0 | sim |
| 2024 | 89 | 17.631 | 17.631 | 17.631 | 0 | sim |
| 2025 | 98 | 19.507 | 19.507 | 19.507 | 0 | sim |
| 2026 | 55 | 10.842 | 10.842 | 10.842 | 0 | **não** (opção do autor) |
| **Total** | **721** | **143.337** | **143.337** | **143.337** | **0** | 132.495 em 2019–2025 |

Constatações:

- **Completude:** em todos os anos, os registros coletados são iguais ao total exato informado pela API (`relation = eq`). Os totais também coincidem com a validação feita antes da coleta (`01-parametros-da-extracao.md`, §5). Não houve variação do índice entre a validação e a coleta.
- **Unicidade:** não houve `_id` repetido nem dentro de um ano nem entre anos. A paginação sem *point-in-time* não gerou duplicatas nesta execução.
- **Datas:** todos os `dataAjuizamento` estão preenchidos e caem no ano da partição.
- **Integridade:** o SHA-256 de todas as 721 páginas confere com o registrado no manifesto.

A unicidade vale para o `_id` do registro na API. Ela **não** comprova unicidade por número de processo nem equivale a contagem de vítimas (CLAUDE.md §4.1). A deduplicação analítica será definida na Silver.

## 3. Ocorrências durante a coleta

| Hora | Ocorrência | Resultado |
|---|---|---|
| 02:00:14 | HTTP 429 | Superado na nova tentativa |
| 02:01:15 | HTTP 504 | Superado na nova tentativa |
| 03:00:00–03:00:03 | HTTP 429 em 3 tentativas consecutivas | O ano de 2020 falhou. A retomada automática (03:02:03) continuou da página 51, sem baixar de novo páginas já gravadas |
| 03:15:02 | HTTP 429 | Superado na nova tentativa |
| 04:19:11 | HTTP 429 | Superado na nova tentativa |

Foi usada **1 das 5** retomadas automáticas. Os 429 se concentraram próximos da virada da hora (ver `03-desempenho-api-coleta.md`, §6.1).

## 4. Execuções descartadas

Nenhuma das execuções abaixo é usada na pesquisa.

| `run_id` | Motivo | Dados |
|---|---|---|
| `bronze-20261018-24c258c` | Interrompida de propósito para ajustar o tamanho de página (100 por página, lento demais) | 26 páginas de 2019 (2.600 registros), preservadas em `work/` |
| `bronze-20261018-12748ce` | Falhou por HTTP 504 com páginas de 1.000 (corte de 60 s do gateway) | Nenhuma página gravada |

## 5. Evidências

- `evidencias/coleta_bronze_20261018/verificacao.json`: resultado da verificação independente, sem identificadores.
- `evidencias/coleta_bronze_20261018/manifest.json`: cópia **sanitizada** do manifesto. O campo `last_cursor` foi removido porque contém o identificador do último processo de cada ano; o original permanece em `work/`.
- Log completo: `work/logs/bronze-20261018-9852486.log` (não versionado).

## 6. Próximo passo

Camada **Silver**: normalizar processos, assuntos, movimentos e complementos; derivar `motivo_inclusao` (núcleo, específica, ambígua ou secundária) e as flags dos marcadores (12195, 12197, 15174, 15180); converter `dataAjuizamento` preservando o original; restringir a análise a 2019–2025.
