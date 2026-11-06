# Datajud/TJPR — coleta Bronze

O projeto implementa o piloto de coleta de metadados públicos do TJPR descrito em `docs/superpowers/specs/2026-09-22-datajud-bronze-pilot-design.md`.

## Ambiente

Use a `.venv` local:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -v
```

As respostas reais, checkpoints, logs e credenciais não são versionados.

## Chave da API

A CLI lê `DATAJUD_API_KEY` de um arquivo `.env` na raiz do projeto (ignorado pelo Git). Copie o modelo e preencha com a chave pública vigente publicada pelo CNJ:

```powershell
Copy-Item .env.example .env
# edite .env:  DATAJUD_API_KEY=<chave vigente>
```

Uma variável de ambiente `DATAJUD_API_KEY` já definida tem precedência sobre o `.env`. A chave pode mudar; consulte https://datajud-wiki.cnj.jus.br/api-publica/acesso/.

## Coleta

Com a raiz do projeto como diretório atual (o `.env` é procurado nela):

Coleta definitiva (TJPR, G1, 2019–2026, catálogo `tjpr_vcm_2026-10-18`):

```powershell
.\.venv\Scripts\datajud-tcc.exe collect --config config/collection.bronze.yaml
```

Piloto (uma página de 100 por ano):

```powershell
.\.venv\Scripts\datajud-tcc.exe collect --config config/collection.example.yaml
```

Opções: `--run-id <id>` para nomear ou retomar uma execução; `--catalog <arquivo.yaml>` para usar outro catálogo (padrão: `config/catalogs/tjpr_vcm_2026-10-18.yaml`); `--query-kind diagnostic` exige um catálogo com `classes_diagnosticas` (ex.: `pvd_cnj_2025-07-17.yaml`).

Todos os parâmetros da extração estão documentados em `docs/artigo/01-parametros-da-extracao.md`.

## Relatório

```powershell
.\.venv\Scripts\datajud-tcc.exe report --run-root <pasta da execução> [--output <arquivo.md>] [--catalog <arquivo.yaml>]
```

Para relatar execuções antigas do piloto, passe `--catalog config/catalogs/pvd_cnj_2025-07-17.yaml`: o relatório recusa um catálogo diferente do registrado no manifesto.

O piloto limita cada partição anual a uma página de 100 registros; a coleta definitiva, a 300 páginas de 200 registros por ano (teto de segurança).

## Orquestração (base operacional)

Coletas incrementais automáticas com Prefect, **fora da base do artigo** (ver `docs/artigo/15-orquestracao-prefect.md`). Instale o extra opcional:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,orquestracao]"
```

Primeira execução manual, informando a marca d'água inicial (a maior `dataHoraUltimaAtualizacao` já coletada, em ISO 8601):

```powershell
.\.venv\Scripts\python.exe -c "from datajud_tcc.orquestracao.fluxos import coleta_incremental; print(coleta_incremental(marca_inicial='2026-10-05T18:00:31.594Z'))"
```

As seguintes partem da marca gravada em `work/estado/marca_dagua_tjpr.json`. Para manter o agendamento semanal ativo (só roda com o computador ligado e este processo aberto):

```powershell
.\.venv\Scripts\python.exe -m datajud_tcc.orquestracao.servir
```

Os testes do orquestrador usam um servidor Prefect temporário e um cliente falso; sem o extra instalado, eles são ignorados.


## Silver (PostgreSQL)

A Silver guarda os dados originais da API normalizados (`docs/artigo/10-modelo-dados-silver.md`). Requer PostgreSQL 16 local com o banco `tcc_datajud`. Neste computador o serviço tem início manual e precisa estar rodando: `Start-Service postgresql-x64-16` (PowerShell como administrador).

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,banco]"
```

Adicione ao `.env` (nunca versionado): `DATABASE_URL=postgresql://tcc:<senha>@localhost:5432/tcc_datajud`. O valor nunca é impresso nem registrado em log.

Comandos:

```powershell
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-esquema        # aplica o esquema (idempotente)
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-carregar --run-root <pasta da execução>
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-marca-dagua    # maior dataHoraUltimaAtualizacao da Silver
```

Os testes de banco têm o marcador `banco` e são pulados sem `DATABASE_URL`, sem `psycopg` ou sem conexão (`pytest -m "not banco"` os exclui).

### Carga inicial manual (ainda não executada)

Carregar as duas execuções da base do artigo, a recoleta de 2026 primeiro (é a menor e serve para medir o tempo real da carga):

```powershell
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-carregar --run-root work/bronze/datajud/tjpr/collected_at=2026-11-05/run_id=bronze2026-20261105-b67187c
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-carregar --run-root work/bronze/datajud/tjpr/collected_at=2026-10-18/run_id=bronze-20261018-9852486
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-marca-dagua
```

Cada execução é carregada com todas as partições; a Silver não marca o que entra na análise (isso é decidido na Gold). Estimativa: cerca de 158 mil registros e 15 milhões de movimentos no total. A saída de `silver-marca-dagua` é a marca inicial do orquestrador (`docs/artigo/15-orquestracao-prefect.md`, §7).

Para cargas longas, mantenha o computador acordado em outro terminal (o script não altera configurações de energia):

```powershell
powershell -NoProfile -File scripts/manter_acordado.ps1 <run_id>
```

O script só termina sozinho quando `work/logs/<run_id>.log` registra o fim do wrapper da coleta. Numa carga da Silver isso não acontece: **encerre-o manualmente (Ctrl+C) quando a carga terminar**.

### Logs

| Onde | O que mostra |
|---|---|
| `prefect server start` e http://127.0.0.1:4200 | Execuções, tarefas, tentativas, logs e *artifacts* (`coleta-incremental`, `carga-silver`) |
| `work/logs/orquestracao.log` | Log do orquestrador e do pacote `datajud_tcc` |
| `work/logs/silver.log` | Carga manual: SHA-256 verificado, registros e movimentos por página, contagens e duração |

O `prefect.toml` na raiz faz o Prefect capturar os logs do pacote `datajud_tcc`. Os logs não contêm DSN, número de processo nem chave da API.
