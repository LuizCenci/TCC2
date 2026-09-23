# Datajud/TJPR Bronze Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um coletor Bronze reproduzível que consulte até 100 processos temáticos de violência doméstica por ano no TJPR/G1 entre 2019 e 2025, preserve as respostas brutas e produza um relatório agregado de viabilidade.

**Architecture:** Um pacote Python separará configuração, catálogo TPU, construção de consultas, transporte HTTP, persistência e orquestração. O piloto usará exatamente o fluxo destinado à carga completa, limitado por `max_pages_per_partition: 1`; dados reais e segredos permanecerão fora do Git.

**Tech Stack:** Python 3.12+, `requests`, `PyYAML`, `jsonschema`, biblioteca padrão (`argparse`, `dataclasses`, `gzip`, `hashlib`, `json`, `pathlib`, `time`, `uuid`) e `pytest`/`responses` para testes.

**Spec:** `docs/superpowers/specs/2026-09-22-datajud-bronze-pilot-design.md`

**Execution method:** Native execution in the current session, selected by the project author. Do not dispatch implementation tasks to subagents; request one independent whole-branch review only after all implementation tasks and verification have finished.

## Global Constraints

- Consultar somente TJPR, primeiro grau, `dataAjuizamento` entre 2019-01-01 e 2026-01-01, particionado por ano.
- Usar página de 100 registros e `max_pages_per_partition: 1` no piloto; ambos devem ser configuráveis.
- Preservar `_source` completo e metadados externos retornados pela API.
- Nunca versionar chave, `.env`, respostas reais, checkpoints, logs identificáveis ou números processuais.
- Tratar cível, penal e infracional em um catálogo versionado, sem forçar natureza única por processo.
- Não usar Prefect, PostgreSQL, PostGIS ou implementar Silver neste incremento.
- O teste real exige opt-in e não pertence à suíte comum.
- Não interpretar processos como vítimas/ocorrências nem município do órgão como local do fato.

## Review Focus

- Configuração com anos invertidos, página fora de 10–10.000 ou diretório fora de `work/` deve falhar antes de qualquer requisição; coberto na Tarefa 2.
- HTTP 200 com JSON malformado, `timed_out: true` ou shard com falha deve falhar sem avançar checkpoint; coberto nas Tarefas 4 e 6.
- HTTP 429 com `Retry-After` deve aguardar o valor indicado sem exceder o máximo configurado; coberto na Tarefa 4.
- Reinício após resposta persistida e antes da atualização final do manifesto não deve duplicar página; coberto nas Tarefas 5 e 6.
- Um processo com assuntos de naturezas distintas deve aparecer em todas as categorias aplicáveis no relatório, sem multiplicar a contagem de processos; coberto na Tarefa 8.

---

## Mapa de arquivos

- `pyproject.toml`: metadados, dependências, comandos e configuração do pytest.
- `.gitignore`: proteção de segredos e artefatos reais.
- `.env.example`: nome da variável `DATAJUD_API_KEY`, sem valor.
- `src/datajud_tcc/config.py`: modelos e validação da configuração.
- `src/datajud_tcc/catalog.py`: leitura e validação do catálogo PVD.
- `src/datajud_tcc/query.py`: intervalos anuais e DSL Elasticsearch.
- `src/datajud_tcc/client.py`: autenticação, transporte, retries e validação da resposta.
- `src/datajud_tcc/bronze.py`: escrita atômica comprimida, leitura e hashes.
- `src/datajud_tcc/metadata.py`: modelos e atualização atômica do manifesto.
- `src/datajud_tcc/collector.py`: paginação, retomada e coordenação das partições.
- `src/datajud_tcc/report.py`: métricas agregadas e Markdown publicável.
- `src/datajud_tcc/cli.py`: comandos `collect` e `report`.
- `config/collection.example.yaml`: piloto aprovado.
- `config/catalogs/pvd_cnj_2025-07-17.yaml`: assuntos PVD e classes diagnósticas.
- `schemas/bronze-response.schema.json`: contrato mínimo da resposta.
- `schemas/run-manifest.schema.json`: contrato do manifesto.
- `tests/fixtures/`: somente respostas sintéticas.
- `tests/unit/` e `tests/integration/`: testes sem rede por padrão.
- `README.md`: instalação, segurança e execução.

### Task 1: Base segura e executável do projeto

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.env.example`
- Create: `src/datajud_tcc/__init__.py`
- Create: `tests/test_repository_safety.py`

**Interfaces:**
- Consumes: nenhuma.
- Produces: pacote importável `datajud_tcc`; variável externa `DATAJUD_API_KEY`; ambiente instalável com `python -m pip install -e .[dev]`.

- [ ] **Step 1: Escrever o teste de segurança que deve falhar**

```python
# tests/test_repository_safety.py
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_tracked_source_does_not_contain_embedded_api_key():
    candidates = [ROOT / ".env.example"]
    text = "\n".join(p.read_text(encoding="utf-8") for p in candidates if p.exists())
    assert "Authorization\": \"APIKey " not in text
    assert "DATAJUD_API_KEY=" in (ROOT / ".env.example").read_text(encoding="utf-8")
```

- [ ] **Step 2: Executar o teste e confirmar a falha**

Run: `python -m pytest tests/test_repository_safety.py -v`

Expected: FAIL porque a credencial está embutida e `.env.example` ainda não existe.

- [ ] **Step 3: Criar a base mínima e neutralizar o script inseguro**

Criar `pyproject.toml` com Python `>=3.12`, dependências `requests>=2.32,<3`, `PyYAML>=6,<7`, `jsonschema>=4.23,<5`, extras de desenvolvimento `pytest>=8,<9` e `responses>=0.25,<1`, pacote sob `src/` e comando `datajud-tcc = datajud_tcc.cli:main`. Criar `.env.example` contendo somente `DATAJUD_API_KEY=`. Como os scripts experimentais antigos já foram removidos, não recriá-los.

Adicionar ao `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
*.py[cod]
work/bronze/
work/checkpoints/
work/logs/
outputs/pilot/*.json
outputs/pilot/*.csv
```

- [ ] **Step 4: Instalar em modo editável e executar o teste**

Run: `python -m pip install -e ".[dev]"`

Run: `python -m pytest tests/test_repository_safety.py -v`

Expected: PASS.

- [ ] **Step 5: Fazer revisão de segredo antes do commit**

Run: `rg -n "APIKey |cDZHY|DATAJUD_API_KEY=.+" -g '!docs/**' -g '!.git/**' .`

Expected: nenhuma credencial; apenas referências seguras ao nome da variável podem aparecer.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .gitignore .env.example src/datajud_tcc/__init__.py tests/test_repository_safety.py
git commit -m "chore: establish secure Python project"
```

### Task 2: Configuração validada e catálogo PVD versionado

**Files:**
- Create: `src/datajud_tcc/config.py`
- Create: `src/datajud_tcc/catalog.py`
- Create: `config/collection.example.yaml`
- Create: `config/catalogs/pvd_cnj_2025-07-17.yaml`
- Create: `tests/unit/test_config.py`
- Create: `tests/unit/test_catalog.py`

**Interfaces:**
- Consumes: variável `DATAJUD_API_KEY` apenas na fronteira CLI/cliente.
- Produces: `CollectionConfig.from_yaml(path: Path) -> CollectionConfig`; `Catalog.load(path: Path) -> Catalog`; `Catalog.subject_codes -> tuple[int, ...]`; `Catalog.natures_for(codes: set[int]) -> frozenset[str]`.

- [ ] **Step 1: Escrever testes para configuração válida e entradas perigosas**

```python
def test_pilot_config_has_seven_years_and_one_page(tmp_path):
    cfg = CollectionConfig.from_mapping(valid_mapping(tmp_path))
    assert cfg.years == tuple(range(2019, 2026))
    assert cfg.page_size == 100
    assert cfg.max_pages_per_partition == 1

@pytest.mark.parametrize("patch", [
    {"years": [2025, 2019]},
    {"page_size": 9},
    {"page_size": 10001},
    {"output_root": "../outside"},
])
def test_invalid_collection_config_is_rejected(tmp_path, patch):
    raw = valid_mapping(tmp_path) | patch
    with pytest.raises(ValueError):
        CollectionConfig.from_mapping(raw)
```

- [ ] **Step 2: Executar os testes de configuração e confirmar falha**

Run: `python -m pytest tests/unit/test_config.py -v`

Expected: FAIL por módulo inexistente.

- [ ] **Step 3: Implementar modelos imutáveis e validação**

Implementar `CollectionConfig` com endpoint exato do TJPR, tribunal `TJPR`, grau `G1`, anos ordenados/únicos, `page_size`, `max_pages_per_partition`, timeouts, tentativas, espera máxima e raízes restritas a `work/`. Caminhos resolvidos que escapem da raiz do projeto devem gerar `ValueError`.

- [ ] **Step 4: Escrever testes do catálogo e de múltiplas naturezas**

```python
def test_catalog_exposes_all_approved_subject_codes(catalog):
    assert set(catalog.subject_codes) == {
        10948, 10949, 11979, 12194, 12196, 14097, 14098,
        14226, 14227, 14228, 14229, 14942, 14943, 14944, 14945,
    }

def test_natures_are_multi_label(catalog):
    assert catalog.natures_for({10948, 10949}) == frozenset({"civel", "penal"})
```

- [ ] **Step 5: Implementar catálogo e arquivos YAML**

Usar uma entrada por código com `codigo`, `tipo: assunto`, `descricao`, `natureza`, `fonte`, `consultado_em`, `vigencia` e `justificativa`. Incluir classes diagnósticas `1268` e `12423` em seção separada. Rejeitar códigos duplicados, naturezas fora de `{civel, penal, infracional}` e fonte/data ausentes.

- [ ] **Step 6: Executar a suíte da tarefa**

Run: `python -m pytest tests/unit/test_config.py tests/unit/test_catalog.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/datajud_tcc/config.py src/datajud_tcc/catalog.py config tests/unit/test_config.py tests/unit/test_catalog.py
git commit -m "feat: add validated collection config and PVD catalog"
```

### Task 3: Consultas anuais determinísticas

**Files:**
- Create: `src/datajud_tcc/query.py`
- Create: `tests/unit/test_query.py`

**Interfaces:**
- Consumes: `CollectionConfig`, `Catalog.subject_codes`, cursor opcional `list[str]`.
- Produces: `year_bounds(year: int) -> tuple[str, str]`; `build_main_query(config, catalog, year, search_after=None) -> dict`; `build_diagnostic_query(...) -> dict`.

- [ ] **Step 1: Escrever testes do intervalo e DSL principal**

```python
def test_2019_query_is_half_open_and_keeps_full_source(config, catalog):
    query = build_main_query(config, catalog, 2019)
    filters = query["query"]["bool"]["filter"]
    assert {"range": {"dataAjuizamento": {"gte": "2019-01-01T00:00:00Z", "lt": "2020-01-01T00:00:00Z"}}} in filters
    assert {"term": {"grau.keyword": "G1"}} in filters
    assert query["size"] == 100
    assert query["sort"] == [{"id.keyword": {"order": "asc"}}]
    assert "_source" not in query

def test_search_after_is_added_without_mutating_base(config, catalog):
    first = build_main_query(config, catalog, 2020)
    second = build_main_query(config, catalog, 2020, ["cursor-1"])
    assert "search_after" not in first
    assert second["search_after"] == ["cursor-1"]
```

- [ ] **Step 2: Executar e confirmar a falha**

Run: `python -m pytest tests/unit/test_query.py -v`

Expected: FAIL por módulo inexistente.

- [ ] **Step 3: Implementar consultas principal e diagnóstica**

A consulta principal usará `terms` em `assuntos.codigo`; a diagnóstica usará `terms` nas classes `1268/12423` e `must_not` para os assuntos principais. Centralizar nomes indexados (`grau.keyword`, `id.keyword`) em constantes para que uma incompatibilidade observada seja corrigida em um único ponto e testada.

- [ ] **Step 4: Executar os testes**

Run: `python -m pytest tests/unit/test_query.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/datajud_tcc/query.py tests/unit/test_query.py
git commit -m "feat: build reproducible annual Datajud queries"
```

### Task 4: Cliente HTTP resiliente e validação de respostas

**Files:**
- Create: `src/datajud_tcc/client.py`
- Create: `schemas/bronze-response.schema.json`
- Create: `tests/unit/test_client.py`

**Interfaces:**
- Consumes: endpoint, API key, timeouts, política de retry e corpo `dict`.
- Produces: `DatajudClient.search(body: dict) -> SearchPage`; exceções `AuthenticationError`, `RateLimitError`, `InvalidResponseError`, `TransientDatajudError`; `SearchPage.raw`, `.hits`, `.next_cursor`, `.total`.

- [ ] **Step 1: Escrever testes de autenticação e página válida**

```python
@responses.activate
def test_search_sends_api_key_and_returns_page(client, valid_response):
    responses.post(client.endpoint, json=valid_response, status=200)
    page = client.search({"size": 100})
    assert page.next_cursor == ["TJPR_1"]
    assert responses.calls[0].request.headers["Authorization"].startswith("APIKey ")
```

- [ ] **Step 2: Escrever testes dos cinco modos críticos de falha**

Cobrir JSON inválido, ausência de `hits.hits`, `timed_out: true`, `_shards.failed > 0` e hit sem `sort` quando a página não está vazia. Em todos, esperar `InvalidResponseError`.

- [ ] **Step 3: Escrever teste de 429 com espera injetada**

```python
@responses.activate
def test_429_honors_retry_after(client_factory, valid_response):
    waits = []
    client = client_factory(sleep=waits.append, max_wait_seconds=30)
    responses.post(client.endpoint, status=429, headers={"Retry-After": "7"})
    responses.post(client.endpoint, json=valid_response, status=200)
    client.search({"size": 100})
    assert waits == [7.0]
```

- [ ] **Step 4: Executar e confirmar falhas**

Run: `python -m pytest tests/unit/test_client.py -v`

Expected: FAIL por interfaces inexistentes.

- [ ] **Step 5: Implementar cliente e schema mínimo**

Usar `requests.Session`, timeout `(connect_timeout, read_timeout)`, espera injetável e mensagens sem a chave. Repetir somente 429, 502, 503, 504 e exceções transitórias de conexão, até `max_attempts`. Falhar imediatamente em 401/403. Limitar `Retry-After` a `max_wait_seconds`.

- [ ] **Step 6: Executar os testes**

Run: `python -m pytest tests/unit/test_client.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/datajud_tcc/client.py schemas/bronze-response.schema.json tests/unit/test_client.py
git commit -m "feat: add resilient Datajud HTTP client"
```

### Task 5: Armazenamento Bronze e manifesto atômicos

**Files:**
- Create: `src/datajud_tcc/bronze.py`
- Create: `src/datajud_tcc/metadata.py`
- Create: `schemas/run-manifest.schema.json`
- Create: `tests/unit/test_bronze.py`
- Create: `tests/unit/test_metadata.py`

**Interfaces:**
- Consumes: `run_root: Path`, ano, página, corpo da consulta e resposta bruta.
- Produces: `BronzeStore.write_page(year, page_number, request_body, response_body) -> PageArtifact`; `BronzeStore.read_response(artifact) -> dict`; `ManifestStore.load_or_create(run_context) -> RunManifest`; `ManifestStore.save(manifest) -> None`.

- [ ] **Step 1: Escrever teste de round-trip e hash**

```python
def test_page_round_trip_is_compressed_and_hashed(tmp_path, valid_response):
    artifact = BronzeStore(tmp_path).write_page(2019, 1, {"size": 100}, valid_response)
    assert artifact.response_path.suffix == ".gz"
    assert len(artifact.sha256) == 64
    assert BronzeStore(tmp_path).read_response(artifact) == valid_response
```

- [ ] **Step 2: Escrever teste de idempotência e colisão**

Regravar conteúdo idêntico no mesmo caminho deve devolver o artefato existente. Conteúdo diferente para página já confirmada deve gerar `ArtifactConflictError`, nunca sobrescrever.

- [ ] **Step 3: Escrever teste de manifesto sem segredo**

Criar manifesto, salvar, validar pelo schema e afirmar que seu JSON não contém `Authorization`, `APIKey` nem o valor de uma chave sintética.

- [ ] **Step 4: Executar e confirmar falhas**

Run: `python -m pytest tests/unit/test_bronze.py tests/unit/test_metadata.py -v`

Expected: FAIL por módulos inexistentes.

- [ ] **Step 5: Implementar escrita canônica, atômica e schemas**

Serializar JSON com chaves ordenadas e UTF-8, comprimir com gzip, calcular SHA-256 dos bytes finais, gravar em arquivo temporário no mesmo diretório e promover com `Path.replace`. Aplicar o mesmo padrão ao manifesto. Persistir caminhos relativos ao `run_root`.

- [ ] **Step 6: Executar os testes**

Run: `python -m pytest tests/unit/test_bronze.py tests/unit/test_metadata.py -v`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/datajud_tcc/bronze.py src/datajud_tcc/metadata.py schemas/run-manifest.schema.json tests/unit/test_bronze.py tests/unit/test_metadata.py
git commit -m "feat: persist immutable Bronze pages and manifests"
```

### Task 6: Coleta paginada e retomável

**Files:**
- Create: `src/datajud_tcc/collector.py`
- Create: `tests/integration/test_collector.py`
- Create: `tests/fixtures/search_page_1.json`
- Create: `tests/fixtures/search_page_2.json`

**Interfaces:**
- Consumes: `CollectionConfig`, `Catalog`, `DatajudClient`, `BronzeStore`, `ManifestStore`.
- Produces: `Collector.collect(run_id: str, query_kind: Literal["main", "diagnostic"]) -> RunManifest`; estados `pending`, `running`, `complete`, `failed` por partição.

- [ ] **Step 1: Escrever teste de duas páginas e cursor**

Configurar `max_pages_per_partition=2`, cliente falso com duas páginas sintéticas e afirmar duas chamadas, segunda consulta com `search_after`, dois arquivos e partição completa.

- [ ] **Step 2: Escrever teste de limite do piloto**

Com `max_pages_per_partition=1`, afirmar somente uma chamada e estado `limited`, não `complete`, quando a primeira página tiver 100 hits.

- [ ] **Step 3: Escrever teste de retomada após persistência**

Preparar página 1 válida no disco e manifesto ainda `running`; reiniciar e afirmar que o coletor verifica hash/cursor, não grava página 1 novamente e solicita apenas a página seguinte.

- [ ] **Step 4: Escrever teste de resposta inválida sem checkpoint**

Fazer `client.search` lançar `InvalidResponseError`; afirmar partição `failed`, cursor inalterado e ausência de arquivo definitivo da página.

- [ ] **Step 5: Executar e confirmar falhas**

Run: `python -m pytest tests/integration/test_collector.py -v`

Expected: FAIL por orquestrador inexistente.

- [ ] **Step 6: Implementar máquina de estados da coleta**

Processar anos em ordem, construir consulta por tipo, salvar página antes de atualizar cursor e atualizar manifesto após cada transição. Uma página vazia conclui a partição; página menor que `page_size` também conclui; atingir o limite com página cheia marca `limited`. Capturar exceções por partição, registrar classe/mensagem sanitizada e continuar somente se `continue_on_partition_error` estiver habilitado.

- [ ] **Step 7: Executar integração e suíte acumulada**

Run: `python -m pytest tests/unit tests/integration/test_collector.py -v`

Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add src/datajud_tcc/collector.py tests/integration/test_collector.py tests/fixtures
git commit -m "feat: orchestrate resumable annual collection"
```

### Task 7: CLI segura para coleta principal e diagnóstico

**Files:**
- Create: `src/datajud_tcc/cli.py`
- Create: `tests/unit/test_cli.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: arquivo de configuração, variável `DATAJUD_API_KEY`, `--run-id` opcional, `--query-kind`.
- Produces: `datajud-tcc collect --config PATH --query-kind main|diagnostic`; códigos de saída 0 sucesso, 2 configuração/credencial, 3 coleta com falha.

- [ ] **Step 1: Escrever testes sem rede da CLI**

```python
def test_collect_refuses_missing_api_key(monkeypatch, capsys):
    monkeypatch.delenv("DATAJUD_API_KEY", raising=False)
    assert main(["collect", "--config", "config/collection.example.yaml"]) == 2
    assert "DATAJUD_API_KEY" in capsys.readouterr().err

def test_collect_never_prints_key(monkeypatch, fake_collector, capsys):
    monkeypatch.setenv("DATAJUD_API_KEY", "segredo-sintetico")
    main(["collect", "--config", "config/collection.example.yaml"])
    assert "segredo-sintetico" not in capsys.readouterr().out
```

- [ ] **Step 2: Executar e confirmar falha**

Run: `python -m pytest tests/unit/test_cli.py -v`

Expected: FAIL por CLI inexistente.

- [ ] **Step 3: Implementar CLI e documentação operacional**

Usar `argparse`, gerar `run_id` UTC mais UUID curto quando ausente e imprimir apenas run ID, estado e caminho do manifesto. Documentar PowerShell:

```powershell
$env:DATAJUD_API_KEY = Read-Host "Cole a chave vigente obtida no CNJ"
datajud-tcc collect --config config/collection.example.yaml --query-kind main
Remove-Item Env:DATAJUD_API_KEY
```

O valor digitado permanece somente no ambiente do processo PowerShell e deve ser removido ao final.

- [ ] **Step 4: Executar testes e ajuda**

Run: `python -m pytest tests/unit/test_cli.py -v`

Run: `datajud-tcc --help`

Expected: testes PASS e ajuda lista `collect`.

- [ ] **Step 5: Commit**

```bash
git add src/datajud_tcc/cli.py tests/unit/test_cli.py README.md
git commit -m "feat: expose safe Bronze collection CLI"
```

### Task 8: Relatório agregado do piloto

**Files:**
- Create: `src/datajud_tcc/report.py`
- Create: `tests/unit/test_report.py`
- Modify: `src/datajud_tcc/cli.py`
- Modify: `README.md`

**Interfaces:**
- Consumes: diretório de execução Bronze, `Catalog`.
- Produces: `build_pilot_summary(run_root: Path, catalog: Catalog) -> PilotSummary`; `write_markdown(summary, destination: Path) -> Path`; comando `datajud-tcc report --run-root PATH`, com destino padrão `outputs/pilot/{run_id}.md` derivado do manifesto.

- [ ] **Step 1: Escrever teste de preenchimento e contagem única**

Criar dois processos sintéticos, um com assuntos cível e penal, e afirmar: `process_count == 2`, naturezas `civel == 1` e `penal == 1`, sem transformar a soma de naturezas em total geral.

- [ ] **Step 2: Escrever teste de privacidade do Markdown**

Usar `_id` e `numeroProcesso` marcadores na fixture e afirmar que nenhum aparece no relatório. Afirmar presença das ressalvas “processos não equivalem a vítimas ou ocorrências” e “município do órgão julgador não representa necessariamente o local do fato”.

- [ ] **Step 3: Escrever teste de campos e metadados ausentes**

Uma resposta sem movimentos, complementos ou código municipal deve aumentar os contadores de ausência, sem descartar o processo. `hits.total.relation: gte` deve ser exibido como limite inferior.

- [ ] **Step 4: Executar e confirmar falhas**

Run: `python -m pytest tests/unit/test_report.py -v`

Expected: FAIL por relatório inexistente.

- [ ] **Step 5: Implementar resumo e renderização**

Percorrer arquivos `.response.json.gz` em streaming por página. Agregar por ano: estado, retornados, total/relação, assuntos, classes, naturezas multilabel, presença de datas/localização/movimentos/complementos, duplicações de `_id` e alertas. Renderizar apenas contagens e percentuais; não incluir amostras de valores identificadores.

- [ ] **Step 6: Integrar comando e executar suíte completa offline**

Run: `python -m pytest -v`

Expected: PASS, sem acessar rede.

- [ ] **Step 7: Commit**

```bash
git add src/datajud_tcc/report.py src/datajud_tcc/cli.py tests/unit/test_report.py README.md
git commit -m "feat: generate privacy-safe pilot report"
```

### Task 9: Verificação real controlada e entrega do parecer

**Files:**
- Create: `tests/integration/test_live_datajud.py`
- Create after execution: relatório `outputs/pilot/{run_id}.md`, nomeado pelo manifesto.
- Modify after findings: `docs/superpowers/specs/2026-09-22-datajud-bronze-pilot-design.md` only if the observed API contract contradicts the approved assumptions.

**Interfaces:**
- Consumes: chave vigente, endpoint público, configuração piloto concluída.
- Produces: respostas locais ignoradas pelo Git, manifesto verificável e relatório agregado versionável após inspeção.

- [ ] **Step 1: Criar teste live explicitamente desabilitado por padrão**

```python
@pytest.mark.live
@pytest.mark.skipif(os.getenv("RUN_DATAJUD_LIVE") != "1", reason="live opt-in")
def test_tjpr_returns_valid_g1_page(live_client, main_query_2019):
    page = live_client.search(main_query_2019 | {"size": 1})
    assert len(page.hits) <= 1
    assert all(hit["_source"]["grau"] == "G1" for hit in page.hits)
```

- [ ] **Step 2: Confirmar que a suíte comum não acessa a rede**

Run: `python -m pytest -m "not live" -v`

Expected: PASS.

- [ ] **Step 3: Executar smoke test com autorização e credencial local**

Run: `$env:RUN_DATAJUD_LIVE='1'; python -m pytest tests/integration/test_live_datajud.py -m live -v`

Expected: PASS, ou falha documentada com HTTP/status sanitizado. Se `grau.keyword` ou outro campo indexado for incompatível, adicionar primeiro uma fixture que reproduza o contrato observado, corrigir a constante e repetir toda a suíte.

- [ ] **Step 4: Executar coleta principal e diagnóstica em run IDs separados**

Run: `datajud-tcc collect --config config/collection.example.yaml --query-kind main`

Run: `datajud-tcc collect --config config/collection.example.yaml --query-kind diagnostic`

Expected: manifestos com sete partições cada; estados `limited`, `complete` ou falha explícita, nunca sucesso silencioso.

- [ ] **Step 5: Gerar e inspecionar o relatório antes de versionar**

Run: `$pilotRun = Get-ChildItem -Directory work/bronze/datajud/tjpr/collected_at=*/run_id=* | Sort-Object LastWriteTime -Descending | Select-Object -First 1; datajud-tcc report --run-root $pilotRun.FullName`

Run: `$pilotReport = Get-ChildItem outputs/pilot/*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1; rg -n "numeroProcesso|_id|[0-9]{20}" $pilotReport.FullName`

Expected: relatório gerado; segunda busca sem identificadores processuais.

- [ ] **Step 6: Verificar repositório e suíte final**

Run: `git status --short`

Run: `python -m pytest -m "not live" -v`

Expected: nenhum arquivo sob `work/` listado; suíte offline PASS.

- [ ] **Step 7: Commit do teste e do relatório sanitizado**

```bash
git add tests/integration/test_live_datajud.py outputs/pilot/*.md
git commit -m "test: validate controlled TJPR pilot collection"
```

## Sequência de aceite

1. Todas as tarefas 1–8 passam sem rede.
2. O teste live é opt-in e não expõe credencial nem conteúdo identificável.
3. A coleta real preserva no máximo uma página de 100 registros por ano e mantém consulta diagnóstica separada.
4. Retomada simulada não duplica artefatos ou páginas.
5. O relatório final contém cobertura, preenchimento, classes, assuntos, naturezas multilabel e limitações explícitas.
6. Divergências observadas na API são registradas como achados e refletidas em teste antes de qualquer ajuste.
