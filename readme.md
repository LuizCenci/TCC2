# Judicialização da violência contra a mulher no Paraná — Datajud/TJPR

Trabalho de Conclusão de Curso (UTFPR, Campus Dois Vizinhos) que analisa a judicialização da violência contra a mulher no Paraná a partir dos metadados públicos do TJPR na API Pública do Datajud (CNJ).

O projeto implementa um pipeline reproduzível na Arquitetura Medalhão:

| Camada | O que faz | Documentação |
|---|---|---|
| Bronze | Coleta paginada da API, com as respostas originais preservadas e SHA-256 por página | `docs/artigo/01`, `06`, `13` |
| Silver | Normalização em PostgreSQL (registros, assuntos, movimentos, complementos); identificadores isolados no esquema `restrito` | `docs/artigo/10`, `17` |
| Gold | Base analítica com regras versionadas, mesorregiões (PostGIS), tempos (Kaplan-Meier), desfechos (Aalen-Johansen) e taxas suavizadas | `docs/artigo/20`, `23`–`26` |
| Publicação | Apenas agregados com supressão de células, com manifesto | `outputs/publicacao/` |
| Orquestração | Prefect: coleta incremental → Silver → Gold → agregados | `docs/artigo/15` |

**Recorte:** TJPR, 1º grau, ajuizamentos de 2019 a 2026 (2026 parcial, até 30/09/2026), somente processos públicos (`nivelSigilo` 0), catálogo temático `config/catalogs/tjpr_vcm_2026-10-18.yaml`. A base reúne 147.002 registros coletados, ou 147.020 processos na Gold.

**Limites de leitura:** os dados contam processos públicos, não vítimas nem ocorrências. A localização é a do órgão julgador, não a do fato. O acervo público é uma fração do total registrado pelo CNJ (`docs/artigo/22-validacao-cnj.md`).

Toda a documentação de parâmetros, decisões e resultados fica em `docs/artigo/` (índice em `docs/artigo/README.md`). O dashboard interativo para a apresentação está descrito na seção "Dashboard" abaixo e em `dashboard/README.md`.

## Dados publicados

`outputs/publicacao/2026-11-05_gold-2026-11-07/` contém os agregados usados no artigo: 12 CSVs e um `manifesto.json` com a versão das regras (`gold-2026-11-07`), a data de corte e o SHA-256 de cada arquivo. Eles não contêm identificadores processuais. As células abaixo de 5 processos (10 por órgão julgador) são suprimidas, há supressão secundária, e as contagens de tempos e desfechos são arredondadas na base 10 (`docs/artigo/25-metodos-e-agregados.md`). O esquema SQL de todas as camadas está em `banco/esquema_completo.sql`, e o backup público do banco (sem números de processo) está na release `dados-2026-11-07`; instruções em `banco/README.md`. As respostas brutas da API ficam apenas locais.

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

Coletas incrementais com Prefect, encadeando coleta, carga na Silver, construção da Gold e agregados (ver `docs/artigo/15-orquestracao-prefect.md`). Coletas sem registros novos não disparam as etapas seguintes. A exportação para `outputs/publicacao/` continua manual, porque é o ponto em que os dados se tornam públicos. As coletas incrementais **não fazem parte da base congelada do artigo**. Instale o extra opcional:

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

### Carga inicial manual (executada em 06/11/2026)

Carregar as duas execuções da base do artigo, a recoleta de 2026 primeiro (é a menor e serve para medir o tempo real da carga):

```powershell
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-carregar --run-root work/bronze/datajud/tjpr/collected_at=2026-11-05/run_id=bronze2026-20261105-b67187c
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-carregar --run-root work/bronze/datajud/tjpr/collected_at=2026-10-18/run_id=bronze-20261018-9852486
.\.venv\Scripts\python.exe -m datajud_tcc.cli silver-marca-dagua
```

Cada execução é carregada com todas as partições; a Silver não marca o que entra na análise (isso é decidido na Gold). Resultado: 157.844 registros (147.020 identificadores distintos), 13.674.340 movimentos e 6.888.510 complementos, em cerca de 9,5 minutos (`docs/artigo/17-carga-inicial-silver.md`). A saída de `silver-marca-dagua` é a marca inicial do orquestrador (`docs/artigo/15-orquestracao-prefect.md`, §7).

Para cargas longas, mantenha o computador acordado em outro terminal (o script não altera configurações de energia):

```powershell
powershell -NoProfile -File scripts/manter_acordado.ps1 <run_id>
```

O script só termina sozinho quando `work/logs/<run_id>.log` registra o fim do wrapper da coleta. Numa carga da Silver isso não acontece: **encerre-o manualmente (Ctrl+C) quando a carga terminar**.

## Gold

Com a Silver carregada, construa a base analítica (idempotente; versão de regras `gold-2026-11-07`, detalhes em `docs/artigo/23-implementacao-gold.md`):

```powershell
.\.venv\Scripts\python.exe -m datajud_tcc.cli gold-construir   # reconstrói ref.* e gold.*
.\.venv\Scripts\python.exe -m datajud_tcc.cli gold-qualidade   # resumo de qualidade
.\.venv\Scripts\python.exe -m datajud_tcc.cli gold-agregados   # taxas, tempos e desfechos (após gold-construir)
.\.venv\Scripts\python.exe -m datajud_tcc.cli gold-exportar    # CSV + manifesto com supressão, em uma pasta nova de outputs/publicacao/
```

Ordem: Silver carregada, depois `gold-construir`, `gold-agregados` e `gold-exportar` (métodos e supressão em `docs/artigo/25-metodos-e-agregados.md`). Em cargas longas, mantenha o PC acordado com `scripts/manter_acordado.ps1 <run_id>` (encerre-o manualmente ao fim, como na Silver). Ciclo rápido de testes: `pytest -m "not gold_lento"`.

A exportação nunca sobrescreve uma pasta existente. Para publicar uma nova versão, confira os arquivos gerados e versione a nova pasta; a pasta citada no artigo permanece inalterada.

## Logs

| Onde | O que mostra |
|---|---|
| `prefect server start` e http://127.0.0.1:4200 | Execuções, tarefas, tentativas, logs e *artifacts* (`coleta-incremental`, `carga-silver`) |
| `work/logs/orquestracao.log` | Log do orquestrador e do pacote `datajud_tcc` |
| `work/logs/silver.log` | Carga manual: SHA-256 verificado, registros e movimentos por página, contagens e duração |

O `prefect.toml` na raiz faz o Prefect capturar os logs do pacote `datajud_tcc`. Os logs não contêm DSN, número de processo nem chave da API.

## Dashboard

App Streamlit em `dashboard/` que exibe os agregados da Gold (exportação `outputs/publicacao/2026-11-05_gold-2026-11-07/`). Execução: `pip install -e ".[dashboard]"` e `streamlit run dashboard/app.py`. Publicação, atualização dos dados e geometria: `dashboard/README.md`; registro no artigo: `docs/artigo/27-dashboard.md`.
