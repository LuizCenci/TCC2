# Recoleta da partição 2026

Status: **verificado** (05/11/2026). Motivo: decisão do autor de **incluir 2026 na análise** (período 2019–2026), com os dados disponíveis até a data da coleta (`01-parametros-da-extracao.md`, §2).

## 1. Identificação

| Item | Valor |
|---|---|
| `run_id` | `bronze2026-20261105-b67187c` |
| Commit do código | `b67187c` |
| Configuração | `config/collection.bronze-2026.yaml`, igual à da coleta definitiva exceto `years: [2026]`; SHA-256 `c73f578b7017402b83e34f22a57d2a07e3fd57a60447caa81edbfdfa31999e42` |
| Catálogo | `tjpr-vcm-2026-10-18` (SHA-256 `df83d3ab…2f245035`), inalterado |
| Hash interno da configuração (`config_hash`) | `323a4998f7e64442254bd9a40602ef08a2e9d334238237b0bdd6a29df8ad0cd8` |
| Início / fim | 05/11/2026 18:52:38 / 19:39:36 (local); cerca de 47 min |
| Armazenamento | `work/bronze/datajud/tjpr/collected_at=2026-11-05/run_id=bronze2026-20261105-b67187c/` (73 páginas, não versionado) |

## 2. Completude (verificação independente)

| Ano | Páginas | Registros coletados | Total da API (`eq`) | IDs únicos | Datas fora do ano | Hashes |
|---|---:|---:|---:|---:|---:|---|
| 2026 | 73 | **14.507** | 14.507 | 14.507 | 0 | conferem |

## 3. Ocorrências

| Hora | Ocorrência | Resultado |
|---|---|---|
| 18:53:01 | HTTP 429 | superado na nova tentativa |
| 19:00:35–19:00:55 | HTTP 429 persistente | partição falhou (`RateLimitError`); **retomada automática** às 19:02:55 a partir da página 17, sem baixar de novo as já gravadas |
| 19:04–19:13 | 5 × HTTP 429 | todos superados na nova tentativa |

Foi usada 1 das 5 retomadas. A concentração de 429 é maior do que em 18/10 e não se limita à virada da hora (`03` §6.1).

## 4. Comparação com a partição 2026 da coleta de 18/10/2026

Comparação por `_id`, só com contagens (`evidencias/coleta_bronze_2026_20261105/comparacao_2026.json`).

| Medida | Valor |
|---|---:|
| Registros em 18/10 | 10.842 |
| Registros em 05/11 | 14.507 |
| Em ambas | 10.824 |
| **Novos** (só em 05/11) | **3.683**, todos com ajuizamento até 18/10 |
| **Saíram do índice público** (só em 18/10) | **18**, ajuizados em jan–jun/2026 |
| Ajuizamento mais recente em 18/10 | 31/07/2026 |
| **Ajuizamento mais recente em 05/11** | **30/09/2026** |
| Data de ajuizamento alterada nos registros comuns | 0 |

Registros novos por mês de ajuizamento: jan 22, fev 24, mar 53, abr 36, mai 51, jun 77, **jul 916, ago 1.535, set 969**.

Registros de 2026 por mês, na base usada: jan 1.743 · fev 1.741 · mar 2.058 · abr 1.725 · mai 1.659 · jun 1.484 · jul 1.593 · ago 1.535 · **set 969**.

## 5. Interpretação

1. **Atraso de indexação.** O índice público chega ao ajuizamento de cerca de 1 a 2 meses antes da data da consulta: 31/07 em 18/10 e 30/09 em 05/11. A última carga do TJPR ao Datajud no recorte foi em 05/10/2026 (`docs/anotações tcc.md`). Meses recentes continuam crescendo a cada carga.
2. **Setembro de 2026 está incompleto** (969, contra 1.484–2.058 em jan–ago). **Agosto parece completo**, mas pode ainda receber registros. Para comparações, o intervalo seguro de 2026 é **janeiro a agosto**.
3. **Registros que saem do índice.** 18 registros (0,17%) presentes em 18/10 não estão mais na API. A explicação provável é a decretação de sigilo ou a reclassificação (hipótese; `12`). O índice público **não é estático**: a base do artigo é um retrato em data definida.
4. **Meses antigos também mudam pouco.** Houve 263 registros novos em jan–jun, ajuizados há meses: são registros enviados com atraso ou cujo sigilo foi retirado.

## 6. Composição da base de análise (2019–2026)

| Partição | Execução | Retrato do índice | Registros |
|---|---|---|---:|
| 2019–2025 | `bronze-20261018-9852486` | 18/10/2026 | 132.495 |
| 2026 | `bronze2026-20261105-b67187c` | 05/11/2026 | 14.507 |
| **Total** | | | **147.002** |

A partição 2026 da execução de 18/10 (10.842 registros) fica preservada na Bronze, mas **é substituída** por esta na análise.

**Limitações a declarar:**
- 2026 é ano parcial: usar janeiro–agosto ou séries mensais;
- as coortes recentes têm acompanhamento curto, com censura nos tempos e desfechos;
- as partições são retratos do índice em datas diferentes (diferença de 18 dias).

## 7. Evidências

- `evidencias/coleta_bronze_2026_20261105/verificacao.json`: verificação independente.
- `evidencias/coleta_bronze_2026_20261105/comparacao_2026.json`: comparação com a partição anterior.
- `evidencias/coleta_bronze_2026_20261105/manifest.json`: manifesto sem `last_cursor`.
- Scripts: `evidencias/scripts/verificar_bronze.py`, `evidencias/scripts/comparar_particao_2026.py`.
- Log: `work/logs/bronze2026-20261105-b67187c.log` (não versionado).
