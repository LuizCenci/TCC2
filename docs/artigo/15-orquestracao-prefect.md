# Orquestração com Prefect

Data: 05/11/2026. Status: escopo **aprovado pelo autor** (incluindo a construção da Gold no orquestrador) e **coleta incremental implementada e testada com dados simulados** (§6). As etapas Silver e Gold estão como interfaces, a implementar com o banco de dados. O Prefect está previsto no projeto original (CLAUDE.md §9).

## 1. Princípio

A **base do artigo é congelada**: coleta definitiva `bronze-20261018-9852486` (2019–2025) mais a recoleta de 2026 (`13`), com uma versão fixa de regras. O orquestrador opera uma **base operacional** separada, que recebe execuções automáticas **fora da base do artigo**. A Silver guarda todas as execuções, sem marcar o que está em análise; quem aplica os critérios de análise é a Gold. Essas execuções servem para validar a automação e como evidência dos critérios de avaliação do pipeline (CLAUDE.md §12).

## 2. O que orquestrar

| Etapa | Orquestrar? | Justificativa |
|---|---|---|
| Coleta definitiva (base do artigo) | Não (manual, já feita) | Evento único, documentado e congelado |
| Coletas incrementais → Bronze | **Sim** | Repetitiva; sujeita a 429/504; precisa de agendamento, retomada e registro |
| Bronze → Silver | **Sim** | Carga idempotente com validação a cada execução |
| Silver → Gold (construção das tabelas) | **Sim** | Transformação determinística por versão de regras (classificação, eventos, tempos, trajetórias, tabelas do dashboard); repetida quando as regras mudam |
| Análise exploratória e clusterização | Não | Trabalho iterativo, em notebook |

## 3. Fluxos propostos

1. **`coleta_incremental`** (agendado, por exemplo semanal):
   - chama o coletor existente como tarefa, uma partição por vez;
   - limite de concorrência 1, por respeito à infraestrutura do CNJ (CLAUDE.md §8);
   - agendamento **fora da virada da hora**, onde os HTTP 429 se concentraram (`03` §6.1);
   - novas tentativas do Prefect com espera longa, para não multiplicar as do cliente.
2. **`carga_silver`** (disparado ao fim de uma coleta concluída):
   - verifica o SHA-256 das páginas;
   - carrega com a chave `(run_id, api_id)`;
   - confere se as contagens da Silver são iguais às do manifesto;
   - publica um relatório de qualidade como *artifact*.
3. **`construcao_gold`** (por versão de regras): `deriv.*` e agregações, regenerado quando a versão de regras muda (`10`).

## 4. Questões a resolver antes de implementar

- **Janela incremental.** Filtrar por `dataAjuizamento` traz processos novos, mas não captura movimentos novos de processos antigos, que são os que atualizam trajetórias e desfechos (`14`). É preciso testar se a API aceita filtro por `dataHoraUltimaAtualizacao` e em que formato.
- **Execução local:** agendamentos só rodam com a máquina ligada e o processo do Prefect ativo (`flow.serve()` ou servidor local). Evitar o Prefect Cloud, para os dados não saírem da máquina. Para o TCC, basta demonstrar algumas execuções registradas.
- **Acoplamento mínimo:** o Prefect apenas chama funções do pacote `datajud_tcc`, e a CLI continua funcionando sem ele. A dependência fica opcional (por exemplo, extra `[orquestracao]` no `pyproject.toml`).
- **Ordem:** implementar e testar a Silver primeiro; só depois envolvê-la em fluxos.

## 5. Evidências que a orquestração pode produzir (CLAUDE.md §12)

- Reexecução sem crescimento indevido de contagens: mesma execução da Bronze carregada duas vezes.
- Retomada após interrupção simulada: coleta interrompida e retomada pelo fluxo.
- Registro de erros, tempos e tentativas por execução (histórico do Prefect).

## 6. Implementação (05/11/2026)

**Janela incremental resolvida.** O teste de 05/11/2026 mostrou que a API aceita filtro por `dataHoraUltimaAtualizacao`, mas **só em ISO 8601**. O campo marca **cargas em lote** do TJPR ao Datajud, não movimentos (`docs/anotações tcc.md`). Ele é usado como **marca d'água**: cada execução coleta os registros com atualização **posterior** à maior data já coletada. Isso traz processos novos e antigos reenviados; dos 14.875 atualizados em outubro/2026, 9.085 tinham ajuizamento entre 2019 e 2025.

| Componente | Arquivo | Função |
|---|---|---|
| Configuração | `config/collection.incremental.yaml` | Mesmo recorte da coleta definitiva (G1, 2019–2026, catálogo `tjpr-vcm-2026-10-18`), sem marca fixa |
| Filtro | `src/datajud_tcc/query.py` | Com `updated_since`, acrescenta `range dataHoraUltimaAtualizacao gt <marca>`; sem ele, a consulta é idêntica à da coleta definitiva |
| Marca d'água | `src/datajud_tcc/orquestracao/marca_dagua.py` | Estado em `work/estado/marca_dagua_tjpr.json` (fora do git), com histórico; **não pode recuar** |
| Fluxos | `src/datajud_tcc/orquestracao/fluxos.py` | `coleta-incremental` → `verificar-completude` → atualização da marca → *artifact*; `carga-silver`; `construcao-gold`; `pipeline-incremental` (encadeia os três e **não carrega a Silver se a coleta falhar**) |
| Etapas | `src/datajud_tcc/orquestracao/etapas.py` | `carregar_silver` implementada (chama `silver.carga.carregar_execucao`); `construir_gold` implementada (chama `gold.construcao.construir_gold`, versão de regras `gold-2026-11-07`; ver `23`) |
| Agendamento | `src/datajud_tcc/orquestracao/servir.py` | Coleta semanal às segundas, 03:17 (fora da virada da hora); pipeline sob demanda; uma execução por vez |

**Proteções:**
- as execuções vão para `work/bronze/datajud/tjpr/incremental/`, separadas da base do artigo;
- uma única nova tentativa da tarefa de coleta, após 10 min, retomando do checkpoint do coletor;
- a marca d'água só é gravada depois da verificação de completude;
- primeira execução exige `marca_inicial` explícita.

**Marca inicial sugerida:** a maior `dataHoraUltimaAtualizacao` das execuções definitivas, para que a primeira coleta incremental traga só o que mudou depois delas.

**Testes** (`tests/integration/test_orquestracao.py`, `tests/unit/test_marca_dagua.py`, `test_config_incremental.py`, `test_query_incremental.py`), com cliente falso e servidor Prefect temporário (`prefect_test_harness`), **sem chamar a API**:
- a marca inicial vira filtro;
- a marca avança e é usada na execução seguinte;
- sem marca, falha sem chamar a API;
- o pipeline encadeia Silver e Gold;
- coleta com falha não dispara a Silver;
- a marca nunca recua.

Resultado: 75 testes passando (1 ignorado, o teste ao vivo).

**Atualização (07/11/2026):** a Gold passa a ser executada pelo pipeline (`construcao_gold` após `carga_silver`), versão de regras `gold-2026-11-07` (`23`). A reconstrução faz TRUNCATE e recria `gold.*`: leitores dessas tabelas ficam brevemente bloqueados durante a construção.

## 7. Sequência de implantação (decidida com o autor em 05/11/2026)

O autor optou por **não** generalizar a carga da Silver para execuções pendentes: cada execução do pipeline carrega só a coleta que acabou de fazer. Daí a ordem obrigatória:

1. implementar o PostgreSQL local e `carregar_silver`;
2. **carga inicial manual**, fora do orquestrador, das execuções da base do artigo, sem marca de análise (a Silver não a guarda): `bronze-20261018-9852486` (partições 2019–2025) e `bronze2026-20261105-b67187c` (2026). A execução de 18/10 tem uma partição 2026 substituída pela recoleta (`13`); ela é carregada junto, como qualquer partição, e a Gold escolhe a versão a usar;
3. marca d'água inicial = maior `dataHoraUltimaAtualizacao` dessas execuções (esperado `2026-10-05T18:00:31.594Z`, a confirmar no momento);
4. só então ligar a orquestração (`servir.py`). Cada execução: coleta incremental → Silver → Gold.

**Não ligar o agendamento antes da Silver.** Coletas feitas antes dela não seriam carregadas depois.

**Versões do mesmo processo.** Execuções incrementais trazem processos antigos reenviados, que já estão na base congelada. Com a chave `(run_id, api_id)`, as versões convivem na Silver; a Gold escolhe qual versão de cada registro entra na análise (critério a definir), e uma visão operacional pode selecionar a mais recente.


## 8. Registros (logs) e validação

| Onde | O que registra |
|---|---|
| Painel do Prefect (`prefect server start`, http://127.0.0.1:4200) | Execuções dos fluxos, tarefas, tentativas, logs e os *artifacts* `coleta-incremental` e `carga-silver` (contagens e segundos) |
| `work/logs/orquestracao.log` | Log do processo `servir.py` e do pacote `datajud_tcc` (arquivo rotativo de 5 MB, 5 cópias) |
| `work/logs/silver.log` | Log da carga manual (`silver-carregar`): páginas, SHA-256 verificado, registros e movimentos por página, contagens finais e duração |

O `prefect.toml` na raiz faz o Prefect capturar os logs do pacote (`extra_loggers = "datajud_tcc"`). Os logs não trazem DSN, número de processo nem `_source.id`. A carga confere o manifesto da Bronze (SHA-256 e contagem de registros) antes de aceitar a execução; os testes de banco cobrem idempotência, hash divergente e registros atípicos.
