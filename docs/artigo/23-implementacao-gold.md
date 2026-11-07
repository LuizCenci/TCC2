# Implementação da Gold (base analítica)

Data: 07/11/2026. Status: **implementada e testada com dados simulados; construção real ainda não executada.** Nenhuma contagem real da Gold é afirmada aqui. Base: [19](19-processo_analise_violencia_mulher_pr.md), [20](20-parametros-gold-e-analise.md), [21](21-fontes-referencia-gold.md), [22](22-validacao-cnj.md).

Versão de regras: `gold-2026-11-07` (`config/gold/regras.yaml`). `construir_gold(conn, versao)` lança `ValueError` se a versão diferir.

## 1. Como executar

Ordem: Silver carregada, depois `gold-construir`.

```powershell
.\.venv\Scripts\python.exe -m datajud_tcc.cli gold-construir
.\.venv\Scripts\python.exe -m datajud_tcc.cli gold-qualidade
```

Conexão só por `DATABASE_URL` (exemplo: `postgresql://tcc:<senha>@localhost:5432/tcc_datajud`), nunca impressa. A construção é idempotente: cada SQL faz `TRUNCATE` da própria saída e reconstrói. Registra uma linha em `controle.execucao_gold` (versão, data, contagens). Em cargas longas, manter o PC acordado (`scripts/manter_acordado.ps1`).

## 2. Tabelas

| Tabela | Conteúdo |
|---|---|
| `ref.municipio`, `ref.mesorregiao` | Municípios do PR e mesorregiões (geometria SIRGAS 2000, EPSG:4674; população feminina do Censo 2022) |
| `ref.classe_tipo` | Classe → tipo de procedimento e júri |
| `ref.assunto_categoria` | Assunto → categoria; `somente_ampliada`, `infracional`, `antecessor` |
| `ref.movimento_fase` | Movimento → fase e subtipo |
| `ref.orgao_especializado` | Órgão → município-sede |
| `ref.quebra_serie` | Quebras de série por categoria |
| `ref.catalogo` | Catálogo temático (código, tipo, grupo, natureza) |
| `gold.fato_processo` | Uma linha por registro selecionado (chave `registro_id`) |
| `gold.processo_categoria` | Categorias por registro (multirrótulo) |
| `gold.fato_evento` | Eventos com fase mapeada |
| `controle.execucao_gold` | Histórico de construções |

Colunas de `gold.fato_processo`: origem (`registro_id`, `run_id`, `data_corte`, `ano_particao`); classe (`classe_codigo`, `tipo_procedimento`, `juri`); órgão e território (`orgao_codigo`, `orgao_especializado`, `municipio_sede_ibge`, `mesorregiao_id`); tempo (`data_ajuizamento`, `ano_ajuizamento`, `mes_ajuizamento`); séries (`serie_estrita`, `feminicidio_tentado`, `infracional`); qualidade (`n_movimentos`, `numero_repetido`, `removido_indice`, `data_ajuizamento_nula`, `reativado`, `evento_antes_ajuizamento`); marcos (`dt_distribuicao`, `dt_decisao_mpu`, `dt_revogacao_mpu`, `dt_recebimento_denuncia`, `dt_primeira_audiencia`, `dt_sentenca`, `dt_transito`, `dt_arquivamento`, `resultado_mpu`); desfecho (`desfecho`, `desfecho_subtipo`, `dt_desfecho`, `duracao_dias`, `censurado`).

Colunas de `gold.fato_evento`: `registro_id`, `seq`, `dt_evento` (timestamptz), `dias_desde_ajuizamento`, `movimento_codigo`, `fase`, `subtipo`, `orgao_codigo`.

## 3. Regras

**Versão do registro.** Para cada `api_id`, entra a versão da execução com maior `concluida_em`; desempate pelo maior `run_id`. Sem filtro de período: os recortes ficam para os agregados.

**`data_corte`.** Por registro: `concluida_em::date` da execução de origem.

**`removido_indice`.** Marcado só por recoletas **completas** da partição. Coleta incremental não marca remoção.

**Séries.** Estrita (`serie_estrita`) e ampliada. Categorias marcadas `somente_ampliada` só entram na ampliada (`20`).

**Categorias.** Dez, multirrótulo (um processo pode ter várias; não somar categorias como processos distintos): as cinco formas do art. 7º da Lei 11.340 (física, psicológica, sexual, patrimonial, moral), ameaça, perseguição, descumprimento de MPU, feminicídio e violência doméstica sem especificação. Nove vêm de `config/gold/ref_assunto_categoria.csv` (gerado por `scripts/gerar_referencias_gold.py`); a décima, `VD_SEM_ESPECIFICACAO`, é derivada em `sql/11_processo_categoria.sql`.

**Território.** Só mesorregião, atribuída pelo município-sede do órgão (`municipio_sede_ibge`). Não há comarca. Município do órgão não é município do fato (CLAUDE.md §4).

**Malha.** API de malhas do IBGE v3 (URL completa em `regras.yaml`), baixada em 07/11/2026, qualidade intermediária, 399 feições, SIRGAS 2000 (EPSG:4674).

**`fato_evento`.** Só movimentos de registros selecionados **com fase mapeada**. O código 12476 ficou fora das fases ("a conferir").

**Marcos.** Primeira data de cada fase, entre eventos válidos (data não nula e `dias_desde_ajuizamento >= 0`). Datas de evento em **UTC**, como a Silver: eventos perto da meia-noite podem cair um dia antes ou depois (hipótese do efeito de borda de um dia, `10` §9; não verificada na Gold).

**Desfecho.** Primeiro evento de julgamento (condenação, absolvição, extinção de punibilidade, prescrição, sem mérito, rejeição de denúncia, arquivamento de investigação). Sem ele: `ENCERRADO_SEM_DESFECHO` se há arquivamento definitivo; senão `EM_ANDAMENTO`, tratado como **censurado** (`censurado`). `duracao_dias` mede do ajuizamento ao desfecho. Ausência de evento não comprova que ele não ocorreu (CLAUDE.md §4).

**`reativado`.** Evento de reativação **estritamente posterior** (`>`) ao arquivamento definitivo.

## 4. Qualidade

Views em `gold.*`, sem identificadores: `qualidade_volume_mensal`, `qualidade_intensidade_registro`, `qualidade_movimentos_duplicados`, `qualidade_sem_mapeamento`, `qualidade_cobertura_referencias`. `gold-qualidade` imprime o resumo. As metas do `19` §10 (`OUTROS` e registros sem categoria abaixo de 2%) ainda **não foram conferidas**: dependem da primeira construção real.

## 5. Desvio registrado

O `19` §5.1 lista `numero_processo` em `gold.fato_processo`. Ele **não** entra: CLAUDE.md §13 e `19` §9 mantêm identificadores fora das camadas analíticas. `numero_processo`, `id_source` e `api_id` não aparecem em `ref.*` nem `gold.*`; o número só é lido de `restrito.identificador` para calcular `numero_repetido`.

## 6. Testes

Testes de banco usam o marcador `banco` (com ROLLBACK). O marcador `gold_lento` roda as transformações sobre a Silver real; para o ciclo rápido: `pytest -m "not gold_lento"`.

## 7. Fica para os próximos planos

Kaplan-Meier, Aalen-Johansen (riscos competitivos), Bayes empírico, taxas por 100 mil mulheres, tabelas de agregados, supressão de células pequenas e dashboard. Também pendente: primeira construção real, com contagens e duração registradas em `docs/artigo/`.
