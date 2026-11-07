# Processo de análise — Violência contra a mulher no Paraná (DataJud/CNJ, 2019–2026)

> **Para o agente de implementação.** Este documento define o processo analítico que orienta a construção da camada **gold**, a integração com **PostGIS** e a exposição via **Python + web**. Siga as etapas **na ordem**: cada etapa produz artefatos que a seguinte consome. Quando algo aqui depender de informação que você não tem (composição oficial das comarcas, códigos TPU exatos), **não invente**: levante na fonte oficial ou nos dados da silver e registre a origem.

---

## 0. Contexto e premissas

- **Fonte:** API pública do DataJud (CNJ), tribunal TJPR, período de 2019 a 2026 (2026 incompleto).
- **Arquitetura atual:** bronze → silver já modelados; trabalho atual é silver → gold.
- **Objetivo do produto:** dashboards interativos sobre a **dinâmica e o tratamento judicial** dos processos de violência contra a mulher no PR, agregados por **comarca/região**.
- **Unidade geográfica:** comarca (não município). O município disponível no DataJud é o da **sede do órgão julgador**, não o local do fato.

### Premissa conceitual obrigatória
Os dados medem o **fluxo do sistema de Justiça**, não a incidência de violência. Toda métrica, título de gráfico e texto da interface deve refletir isso ("processos judiciais", "medidas protetivas decididas"), e **nunca** "casos de violência" ou "onde há mais violência".

---

## 1. Catálogo de perguntas (contrato analítico)

**Entregável:** `docs/catalogo_perguntas.md` (ou tabela equivalente), com 10 a 15 perguntas.

Para cada pergunta, registre:

| Campo | Descrição |
|---|---|
| `id` | Identificador (ex.: `Q01`) |
| `eixo` | Volume, Tempo, Fluxo, Desfecho, Proteção, Desigualdade |
| `pergunta` | Em linguagem natural |
| `metrica` | Fórmula exata |
| `unidade_contagem` | Processo, evento, processo×assunto etc. |
| `tipo_procedimento` | Quais tipos entram (ver etapa 2) |
| `recortes` | Comarca, região, ano, categoria… |
| `metodo` | Ver etapa 6 |
| `tabela_gold` | Tabela/view que atende a pergunta |

Perguntas de partida (refinar com o responsável pelo projeto):

| Eixo | Pergunta | Métrica |
|---|---|---|
| Volume | Como evolui a entrada de processos por comarca? | Processos novos por 100 mil mulheres/ano |
| Tempo | Quanto tempo leva da distribuição à sentença? | Tempo mediano (Kaplan-Meier) |
| Fluxo | Quais caminhos os processos percorrem? | Variantes de fluxo, tempo entre fases |
| Desfecho | Como os processos terminam? | % condenação, absolvição, extinção, prescrição, arquivamento |
| Proteção | Quanto tempo leva a decisão de uma medida protetiva? | Tempo até a decisão da MPU |
| Desigualdade | Comarcas com e sem vara especializada diferem? | Comparação de tempos e desfechos |

**Regra:** métrica que não está no catálogo não entra no dashboard. Toda tabela gold deve atender a pelo menos uma pergunta do catálogo.

---

## 2. Unidades de análise e regras de contagem

**Entregável:** `docs/regras_contagem.md` + coluna `tipo_procedimento` na gold.

### 2.1 Tipo de procedimento (derivado da classe processual)
Separar, no mínimo:
- `MPU`: medidas protetivas de urgência (Lei Maria da Penha)
- `INQUERITO`: inquéritos e procedimentos investigatórios
- `ACAO_PENAL`: ações penais (com denúncia, instrução, sentença)
- `EXECUCAO`: execução penal
- `RECURSO`: segundo grau / recursal
- `OUTROS`

Monte o mapeamento `classe.codigo → tipo_procedimento` a partir das classes **que de fato aparecem na silver**, em uma tabela versionada (`ref_classe_tipo`).

**Proibido:** calcular tempo médio ou taxa de desfecho misturando tipos de procedimento. As análises de tempo e de desfecho são sempre **estratificadas por tipo**.

### 2.2 Decisões que precisam estar documentadas
- **Múltiplos assuntos por processo:** definir se há um assunto principal ou se a contagem é por processo×categoria (nesse caso, avisar na interface que a soma pode passar de 100%).
- **Duplicidade:** o mesmo número de processo em graus/instâncias diferentes. Definir a chave de deduplicação (ex.: `numeroProcesso + grau`) e a regra de qual registro prevalece.
- **Vínculo MPU ↔ ação penal:** com dados públicos, em geral não é possível ligar os dois de forma confiável. Tratar como processos independentes e registrar a limitação.
- **Processo sem movimento terminal:** classificar como `em_andamento` (censurado), e não como desfecho.

---

## 3. Auditoria de qualidade

**Entregável:** `gold.qualidade_*` (tabelas/views) + relatório `docs/qualidade_dados.md`.

Medir e persistir, no mínimo:
- % de processos sem movimentos; distribuição do nº de movimentos por processo.
- Movimentos com data anterior ao ajuizamento ou posterior à data de extração.
- Movimentos duplicados (mesmo código + mesma data/hora no mesmo processo).
- Uso de códigos genéricos (despacho/decisão sem complemento) por órgão julgador.
- **Média de movimentos por processo, por órgão julgador**: é o indicador de *intensidade de registro*. Diferenças grandes entre varas indicam que parte da "diferença de tratamento" pode ser só diferença de registro.
- Processos com classe/assunto nulo ou fora da TPU.
- Volume por ano e por mês, para detectar lacunas de carga (meses zerados, quedas abruptas).

**Regra:** os indicadores de qualidade por comarca devem estar disponíveis na gold e, idealmente, visíveis no dashboard.

---

## 4. Taxonomias (núcleo da camada gold)

**Entregáveis:** tabelas de referência versionadas, com `versao`, `vigencia_inicio`, `vigencia_fim`, `fonte` e `observacao`.

### 4.1 `ref_assunto_categoria`: assunto (TPU) → categoria analítica
Categorias sugeridas (ajustar aos assuntos presentes na silver):
- violência física (lesão corporal no contexto doméstico)
- violência psicológica
- ameaça
- perseguição
- violência sexual
- violência patrimonial
- descumprimento de medida protetiva
- feminicídio (consumado/tentado)
- outros/não classificado

### 4.2 `ref_movimento_fase`: movimento (TPU) → fase/marco
Fases sugeridas:
- `DISTRIBUICAO`
- `DECISAO_MPU` (deferimento / indeferimento / parcial)
- `RECEBIMENTO_DENUNCIA`
- `AUDIENCIA`
- `SENTENCA` com subtipo: `CONDENATORIA`, `ABSOLUTORIA`, `EXTINCAO_PUNIBILIDADE`, `PRESCRICAO`, `OUTRA`
- `TRANSITO_JULGADO`
- `ARQUIVAMENTO`
- `BAIXA`
- `OUTRO` (movimentos sem valor analítico)

Usar também `complementosTabelados` quando necessário para distinguir o subtipo (ex.: tipo de sentença).

### 4.3 Comparabilidade temporal
Entre 2019 e 2026 houve mudanças legais e de tabela que criam **quebras de série**, entre elas: inclusão dos crimes de perseguição e violência psicológica (2021) e o feminicídio como crime autônomo (2024), além de atualizações da própria TPU. Para cada categoria afetada:
- registrar a data da quebra em `ref_quebras_serie`;
- sinalizar a quebra nos gráficos de série temporal.

---

## 5. Modelo da camada gold

**Entregável:** DDL + transformações versionadas (SQL/dbt/Python), reexecutáveis do zero a partir da silver.

### 5.1 `gold.fato_processo` (uma linha por processo deduplicado)
Colunas mínimas:
- `processo_id`, `numero_processo`, `grau`
- `classe_codigo`, `tipo_procedimento`
- `categoria_principal` (+ tabela ponte `gold.processo_categoria`, se houver múltiplas)
- `orgao_julgador_id`, `comarca_id`, `municipio_sede_ibge`
- `data_ajuizamento`, `ano_ajuizamento`
- datas de marcos: `dt_decisao_mpu`, `dt_recebimento_denuncia`, `dt_primeira_audiencia`, `dt_sentenca`, `dt_transito`, `dt_arquivamento`, `dt_baixa`
- `desfecho` (enum alinhado a 4.2) ou `EM_ANDAMENTO`
- `dt_desfecho`
- `duracao_dias` (até o desfecho ou até a data de corte)
- `censurado` (bool: `true` se não houve desfecho até a data de corte)
- `data_corte` (data da extração)
- `n_movimentos`, `flag_qualidade` (bitmask ou colunas booleanas)

### 5.2 `gold.fato_evento` (event log para process mining)
- `processo_id`, `seq`, `dt_evento`, `movimento_codigo`, `fase`, `subtipo`, `orgao_julgador_id`
- Ordenação estável por (`dt_evento`, `seq`).

### 5.3 `gold.dim_comarca` (PostGIS)
- `comarca_id`, `nome`, `regiao`, `entrancia` (se disponível)
- `geom` (MultiPolygon, SRID consistente, por exemplo 4674/SIRGAS 2000, com reprojeção para a web quando necessário)
- `vigencia_inicio`, `vigencia_fim`
- `possui_vara_especializada` (com vigência)
- População feminina por ano em `gold.dim_comarca_populacao (comarca_id, ano, pop_fem)`

**Construção da geometria:** juntar (`ST_Union`) as malhas municipais do IBGE de acordo com a **composição oficial das comarcas do TJPR** (comarca sede + municípios/termos vinculados). Todo município do PR deve pertencer a exatamente uma comarca em cada período. Validar com:
- nenhum município sem comarca;
- nenhum município em duas comarcas no mesmo período;
- soma das áreas das comarcas = área do estado (tolerância pequena).

**Atenção:** a composição muda no tempo (instalação/reorganização de comarcas). Registrar a fonte (ato/resolução do TJPR) e a vigência.

### 5.4 Mapeamento órgão julgador → comarca
Tabela `ref_orgao_comarca`, construída a partir do `codigoMunicipioIBGE` e do nome do órgão julgador, revisada manualmente nos casos ambíguos. Órgãos sem mapeamento devem aparecer na auditoria (etapa 3), não ser descartados silenciosamente.

### 5.5 Agregados para a interface
Views materializadas por `comarca × ano × tipo_procedimento × categoria`, com:
- `n_processos`, `taxa_100k_mulheres`, `taxa_suavizada` (ver 6.4)
- mediana de tempo (KM) e intervalo
- distribuição de desfechos
- indicadores de qualidade
- `n` sempre presente ao lado de taxas e percentuais

---

## 6. Métodos por tipo de pergunta

### 6.1 Volume e taxas
- Sempre normalizar pela **população feminina** da comarca no ano.
- Contagens absolutas só como informação complementar, nunca como cor de mapa.
- **2026 é ano parcial:** marcar visualmente; não comparar com anos fechados sem anualizar ou sem explicitar o corte.

### 6.2 Tempos: análise de sobrevivência (obrigatório)
- **Não usar média nem mediana apenas de processos encerrados.** Isso subestima os tempos, sobretudo nos anos recentes, e cria uma falsa tendência de melhora.
- Usar **Kaplan-Meier** com `duracao_dias` e `censurado`, estratificado por `tipo_procedimento` (e por comarca/região/ano quando houver *n* suficiente).
- Reportar a mediana e o intervalo de confiança; se a mediana não for alcançada, reportar isso (não estimar).
- Biblioteca sugerida: `lifelines`.

### 6.3 Desfechos: riscos competitivos
- Condenação, absolvição, extinção/prescrição e arquivamento competem entre si.
- Usar **incidência acumulada** (Aalen-Johansen) em vez de 1 − KM por desfecho.
- A **prescrição** deve ser destacada como indicador de tratamento.

### 6.4 Espacial
- Comarcas pequenas produzem taxas instáveis. Aplicar **suavização Bayes empírica** (global ou espacial) antes de mapear; manter a taxa bruta disponível em tooltip.
- Oferecer a visão agregada por **região** como alternativa.
- Autocorrelação espacial (Moran global, LISA) apenas sobre taxas suavizadas, e como análise complementar.
- Bibliotecas sugeridas: `geopandas`, `esda`/`libpysal` (PySAL).

### 6.5 Fluxo: process mining
- Usar `gold.fato_evento` como event log (case = `processo_id`, activity = `fase`, timestamp = `dt_evento`).
- Produzir: variantes mais frequentes, tempo entre fases, gargalos, comparação de fluxos entre grupos de comarcas.
- Filtrar movimentos com fase `OUTRO` para reduzir o ruído.
- Biblioteca sugerida: `pm4py`.

### 6.6 Tendências temporais
- Considerar a sazonalidade (mensal) e o período de pandemia (2020–2021).
- Sinalizar as quebras de série (4.3).
- Análises de "efeito" de mudanças legais (séries temporais interrompidas) só como exploração, sem linguagem causal.

---

## 7. Validação

**Entregável:** `docs/validacao.md`.

- Comparar os totais anuais (por tipo de procedimento) com os painéis do CNJ sobre violência doméstica, o relatório Justiça em Números e as estatísticas publicadas pelo TJPR.
- Divergências não precisam ser zero, mas precisam estar **explicadas** (filtro de classe, deduplicação, data de corte, mapeamento de comarca).
- Testes de sensibilidade: as conclusões principais se mantêm ao mudar a regra de deduplicação, o período ou o assunto principal?
- Testes automatizados nas transformações:
  - unicidade de `processo_id` em `fato_processo`;
  - `dt_desfecho >= data_ajuizamento`;
  - `censurado = (desfecho = 'EM_ANDAMENTO')`;
  - todo `comarca_id` existe em `dim_comarca`;
  - geometrias válidas (`ST_IsValid`).

---

## 8. Interface (somente após as etapas 1–7)

- Cada gráfico responde a uma pergunta do catálogo (`id` rastreável).
- Mostrar `n` junto de toda taxa ou percentual; sinalizar amostras pequenas.
- Títulos e legendas usam "processos judiciais", nunca "casos de violência".
- Exibir o contexto das comarcas (vara especializada, volume, qualidade de registro) ao lado das comparações de tempo e desfecho, para evitar leitura causal.
- Número de filtros enxuto; evitar combinações livres de muitos filtros.
- Nota metodológica acessível na própria interface (fonte, data de corte, limitações, quebras de série).

---

## 9. Privacidade (requisito obrigatório)

Muitos processos desse tema tramitam em segredo de justiça. Mesmo com metadados, filtros finos podem permitir reidentificação em comarcas pequenas.

- Definir um **tamanho mínimo de célula** (sugestão: suprimir contagens < 5; avaliar até 10) e aplicá-lo **no backend/API**, não apenas no frontend.
- Supressão secundária quando o valor suprimido puder ser obtido por diferença (total − demais células).
- Não expor `numero_processo` nem nenhum identificador individual na interface ou na API pública.
- Não expor a `fato_evento` em nível de processo pela API pública; apenas agregados.

---

## 10. Ordem de execução e critérios de pronto

| # | Etapa | Pronto quando |
|---|---|---|
| 1 | Catálogo de perguntas | Aprovado pelo responsável; cada pergunta com métrica e unidade |
| 2 | Regras de contagem e tipo de procedimento | `ref_classe_tipo` cobre 100% das classes da silver |
| 3 | Auditoria de qualidade | Relatório gerado; problemas críticos com decisão registrada |
| 4 | Taxonomias | `ref_assunto_categoria` e `ref_movimento_fase` cobrem os códigos da silver (não classificados < limite acordado, ex.: 2% dos registros) |
| 5 | Gold + PostGIS | Testes da etapa 7 passando; geometrias validadas |
| 6 | Métodos | Notebooks/scripts reproduzíveis gerando os agregados |
| 7 | Validação | Divergências com fontes oficiais explicadas |
| 8 | Interface | Toda visualização rastreável a uma pergunta; nota metodológica publicada |
| 9 | Privacidade | Supressão aplicada e testada na API |

**Não iniciar a interface (etapa 8) antes de concluir as etapas 2 e 4.** Mudanças de definição nessas etapas se propagam até a tela e geram retrabalho.

---

## 11. Riscos conhecidos (manter visíveis)

1. **Viés de censura** nos tempos, se a etapa 6.2 não for seguida.
2. **Mistura de tipos de procedimento** distorcendo tempos e desfechos.
3. **Diferença de registro entre varas** confundida com diferença de tratamento.
4. **Taxas instáveis** em comarcas pequenas dominando os extremos do mapa.
5. **Quebras de série** por mudança legal/TPU lidas como tendência real.
6. **Leitura causal** de comparações entre comarcas.
7. **Reidentificação** por filtros finos.
8. **Leitura do dado judicial como incidência de violência.**
