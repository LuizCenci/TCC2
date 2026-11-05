# Orquestração com Prefect — escopo proposto

Data: 05/11/2026. Status: **proposta de trabalho**, ainda não implementada. Discutida com o autor; o Prefect está previsto no projeto original (CLAUDE.md §9).

## 1. Princípio

A **base do artigo é congelada**: coleta definitiva `bronze-20261018-9852486` (2019–2025) mais a recoleta de 2026 (`13`), com uma versão fixa de regras. O orquestrador opera uma **base operacional** separada, que recebe execuções automáticas **fora da análise** (`em_analise = false`). Essas execuções servem para validar a automação e como evidência dos critérios de avaliação do pipeline (CLAUDE.md §12).

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
