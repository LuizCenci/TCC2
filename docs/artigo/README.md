# Documentação para o artigo

Esta pasta reúne a documentação e os relatórios que fundamentam a metodologia e os resultados do artigo. Cada documento indica o próprio status: decisão, achado verificado ou recomendação.

| Documento | Conteúdo | Status |
|---|---|---|
| [01-parametros-da-extracao.md](01-parametros-da-extracao.md) | **Referência da metodologia.** Todos os parâmetros da coleta Bronze: fonte, período (coleta e análise 2019–2026; até 18/10 a análise era 2019–2025), grau, critério temático com todos os códigos TPU, paginação, robustez, volumes e reprodução. | Decidido (18/10/2026) |
| [02-analise-exploratoria-parametros.md](02-analise-exploratoria-parametros.md) | Análise por agregações que fundamentou as escolhas do documento 01. | Verificado (17/10/2026) |
| [03-desempenho-api-coleta.md](03-desempenho-api-coleta.md) | Latência da API, testes de isolamento e ajuste do tamanho de página. | Verificado (18/10/2026) |
| [06-resultado-coleta-bronze.md](06-resultado-coleta-bronze.md) | Resultado da coleta Bronze definitiva: completude por ano, unicidade, integridade, ocorrências e execuções descartadas. | Verificado (18/10/2026) |
| [07-o-que-cada-assunto-traz.md](07-o-que-cada-assunto-traz.md) | Exemplos por código, tipos de procedimento trazidos, impossibilidade de ligar processos, códigos de decisão de medida protetiva e recomendação de categorias analíticas. | Verificado (§1–6) + recomendação (§7–8), 23/10/2026 |
| [08-viabilidade-movimentos-comarcas.md](08-viabilidade-movimentos-comarcas.md) | Viabilidade de indicadores com movimentos (tempos por sobrevivência, eventos por código SGT), N por comarca e anomalias que afetam as séries 2019–2020. | Verificado + recomendação, 23/10/2026 |
| [09-roteiro-consulta-juridica.md](09-roteiro-consulta-juridica.md) | Roteiro de consulta a advogado(a)/servidor(a) do TJPR, perguntas priorizadas, lacunas da análise e tabela para registrar as respostas. | Roteiro (23/10/2026) |
| [10-modelo-dados-silver.md](10-modelo-dados-silver.md) | Proposta de modelo de dados da Silver: esquemas, diagramas ER (Mermaid), dicionário, flags de qualidade, fluxo de carga e decisões em aberto. | Proposta (23/10/2026); dados originais implementados (05/11/2026) |
| [11-revisao-literatura.md](11-revisao-literatura.md) | Levantamento inicial de trabalhos relacionados (Datajud/jurimetria, SINAN/SIM, BOs), com grau de verificação e lacunas. | Levantamento (01/11/2026) |
| [12-resumo-cnj-2022-medidas-protetivas.md](12-resumo-cnj-2022-medidas-protetivas.md) | Resumo do relatório CNJ/Instituto Avon/Consórcio LMP (2022) sobre MPUs no Datajud; números do TJPR (≈83% em sigilo nível 2; só ≈5% públicos) e implicações para o TCC. | Resumo (01/11/2026) |
| [13-recoleta-2026.md](13-recoleta-2026.md) | Recoleta da partição 2026 (05/11/2026): completude, comparação com a coleta de 18/10, atraso de indexação e composição da base 2019–2026. | Verificado (05/11/2026) |
| [14-viabilidade-trajetorias.md](14-viabilidade-trajetorias.md) | Desfecho derivado por código de movimento, trajetórias multicanal e clusterização: viabilidade e cuidados. | Verificado (§1–3) + proposta, 05/11/2026 |
| [15-orquestracao-prefect.md](15-orquestracao-prefect.md) | Orquestração com Prefect: escopo, coleta incremental por marca d'água e implementação. | Implementado (coleta e Silver); Gold como interface, 05/11/2026 |
| [16-auditoria-conformidade-artigo.md](16-auditoria-conformidade-artigo.md) | Auditoria do que está implementado e documentado em relação ao artigo (fonte oficial) e ao CLAUDE.md: conformidades, divergências e prioridades. | Verificado (05/11/2026) |
| [17-carga-inicial-silver.md](17-carga-inicial-silver.md) | Carga real das duas execuções da base na Silver: contagens, duração, verificações e marca d'água inicial do orquestrador. | Verificado (06/11/2026) |
| [19-processo_analise_violencia_mulher_pr.md](19-processo_analise_violencia_mulher_pr.md) | Processo analítico que orienta a Gold, o PostGIS e a interface: catálogo de perguntas, regras de contagem, qualidade, taxonomias, métodos, validação e privacidade (escrito pelo autor). | Orientação do autor (07/11/2026) |
| [20-parametros-gold-e-analise.md](20-parametros-gold-e-analise.md) | Parâmetros da Gold e da análise: conciliação com o `19`, decisões C1–C8, catálogo Q01–Q15 e parâmetros fixos. | Decidido (07/11/2026) |
| [21-fontes-referencia-gold.md](21-fontes-referencia-gold.md) | Fontes de referência: IBGE (mesorregiões, população feminina do Censo 2022), marcos legais, órgãos especializados e as tabelas de tipos, categorias e fases. | Verificado + aprovado (07/11/2026) |
| [22-validacao-cnj.md](22-validacao-cnj.md) | Validação externa contra os painéis do CNJ: cobertura do acervo público por tipo de procedimento, de 2019 a 2026. | Verificado (07/11/2026) |
| [23-implementacao-gold.md](23-implementacao-gold.md) | Implementação da Gold: tabelas, regras de versão, séries, categorias, marcos, desfecho e censura, malha, desvio sobre `numero_processo` e pendências. | Implementada, testada com dados simulados (07/11/2026) |
| [24-construcao-inicial-gold.md](24-construcao-inicial-gold.md) | Primeira construção real da Gold: duração, contagens, metas de cobertura, distribuições descritivas e observações para o plano de métodos. | Verificado (07/11/2026) |
| [25-metodos-e-agregados.md](25-metodos-e-agregados.md) | Tabelas `agg_*` (perguntas, unidade, denominador, limitações), métodos (Bayes empírico, Kaplan-Meier, Aalen-Johansen), supressão e exportação. | Implementado, construção real pendente (08/11/2026) |
| [26-primeira-construcao-agregados.md](26-primeira-construcao-agregados.md) | Primeira construção dos agregados e exportação: durações, linhas por tabela e primeiros resultados descritivos (tempos, desfechos, taxas, cobertura). | Verificado (07/11/2026) |
| [../exemplos/exemplos_json_por_codigo.md](../exemplos/exemplos_json_por_codigo.md) | Inventário de todos os campos da API e os 3 primeiros registros de cada código no JSON original (só identificadores mascarados). | Verificado (24/10/2026) |
| [../anotações tcc.md](../anotações%20tcc.md) | Divergência entre a documentação e o formato real de `dataAjuizamento`. | Verificado (03/10/2026) |
| [04-sinan-exploracao-pr-2023-2024.md](04-sinan-exploracao-pr-2023-2024.md) | Exploração do SINAN Violência (DATASUS), PR 2023–2024. | Exploratório |
| [05-quadro-comparativo-sinan-datajud.md](05-quadro-comparativo-sinan-datajud.md) | Quadro comparativo dos sistemas de registro e encaminhamentos do SINAN. | Recomendação (uso do SINAN pendente de aprovação do orientador) |

## Evidências (`evidencias/`)

| Pasta | Conteúdo |
|---|---|
| `datajud_agregacoes_20261017/` | Consultas e respostas das agregações (`size: 0`); sem documentos de processos. |
| `sgt_tpu_20261018/` | Nomes, hierarquia e glossário da TPU obtidos no webservice SGT/CNJ. |
| `validacao_filtro_20261018/` | Contagem exata por ano com a consulta gerada pelo código e volumes por grupo do catálogo. |
| `desempenho_api_20261018/` | Tempos do servidor por variante de consulta. |
| `coleta_bronze_20261018/` | Verificação independente da coleta e manifesto sanitizado (sem identificadores). |
| `exemplos_assuntos_20261023/` | Exemplos sem identificadores, perfis por código, tipo de classe × grupo, movimentos de medida protetiva. |
| `movimentos_viabilidade_20261023/` | Hierarquia SGT dos movimentos, eventos, Kaplan-Meier, N por sede e investigação das anomalias de 2019–2020 (só agregados). |
| `coleta_bronze_2026_20261105/` | Verificação da recoleta de 2026, comparação com a partição anterior e manifesto sanitizado. |
| `teste_ultima_atualizacao_20261105/` | Teste do filtro por `dataHoraUltimaAtualizacao` e distribuição das cargas em lote. |
| `trajetorias_viabilidade_20261105/` | Desfechos derivados e variantes de trajetória (só agregados). |
| `scripts/` | Scripts que produziram as evidências. Executar a partir da raiz do projeto com `.venv`; os que importam `q`/`sgt` recebem `docs/artigo/evidencias/scripts` como primeiro argumento. Não imprimem a chave da API. |

Dados brutos (Bronze, SINAN) ficam em `work/` e não são versionados.
