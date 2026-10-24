# Documentação para o artigo

Esta pasta reúne a documentação e os relatórios que fundamentam a metodologia e os resultados do artigo. Cada documento indica o próprio status: decisão, achado verificado ou recomendação.

| Documento | Conteúdo | Status |
|---|---|---|
| [01-parametros-da-extracao.md](01-parametros-da-extracao.md) | **Referência da metodologia.** Todos os parâmetros da coleta Bronze: fonte, período (coleta 2019–2026, análise 2019–2025), grau, critério temático com todos os códigos TPU, paginação, robustez, volumes e reprodução. | Decidido (18/10/2026) |
| [02-analise-exploratoria-parametros.md](02-analise-exploratoria-parametros.md) | Análise por agregações que fundamentou as escolhas do documento 01. | Verificado (17/10/2026) |
| [03-desempenho-api-coleta.md](03-desempenho-api-coleta.md) | Latência da API, testes de isolamento e ajuste do tamanho de página. | Verificado (18/10/2026) |
| [06-resultado-coleta-bronze.md](06-resultado-coleta-bronze.md) | Resultado da coleta Bronze definitiva: completude por ano, unicidade, integridade, ocorrências e execuções descartadas. | Verificado (18/10/2026) |
| [07-o-que-cada-assunto-traz.md](07-o-que-cada-assunto-traz.md) | Exemplos por código, tipos de procedimento trazidos, impossibilidade de ligar processos, códigos de decisão de medida protetiva e recomendação de categorias analíticas. | Verificado (§1–6) + recomendação (§7–8), 23/10/2026 |
| [08-viabilidade-movimentos-comarcas.md](08-viabilidade-movimentos-comarcas.md) | Viabilidade de indicadores com movimentos (tempos por sobrevivência, eventos por código SGT), N por comarca e anomalias que afetam as séries 2019–2020. | Verificado + recomendação, 23/10/2026 |
| [09-roteiro-consulta-juridica.md](09-roteiro-consulta-juridica.md) | Roteiro de consulta a advogado(a)/servidor(a) do TJPR, perguntas priorizadas, lacunas da análise e tabela para registrar as respostas. | Roteiro (23/10/2026) |
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
| `scripts/` | Scripts que produziram as evidências. Executar a partir da raiz do projeto com `.venv`; os que importam `q`/`sgt` recebem `docs/artigo/evidencias/scripts` como primeiro argumento. Não imprimem a chave da API. |

Dados brutos (Bronze, SINAN) ficam em `work/` e não são versionados.
