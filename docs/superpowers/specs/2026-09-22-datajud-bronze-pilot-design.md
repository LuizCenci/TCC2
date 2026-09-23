# Coleta Bronze do Datajud/TJPR — desenho do piloto

## 1. Objetivo

Construir a primeira etapa de um pipeline reproduzível para coletar metadados públicos de processos de violência doméstica contra a mulher no TJPR. O piloto deve espelhar a arquitetura pretendida para a carga completa, com volume reduzido exclusivamente por configuração.

O piloto abrangerá os anos completos de 2019 a 2025, primeiro grau, com até uma página de 100 registros por ano na consulta principal. Ele validará acesso, estrutura, cobertura, paginação, persistência e retomada. Os dados coletados não constituirão amostra estatisticamente representativa e não serão usados, isoladamente, para conclusões substantivas sobre a violência no Paraná.

## 2. Decisões aprovadas

- Tribunal: TJPR.
- Grau inicial: primeiro grau (`G1`), com confirmação do valor observado na API.
- Período: 2019–2025, usando `dataAjuizamento` e intervalos anuais não sobrepostos.
- Tema: processos classificados como violência doméstica contra a mulher segundo catálogo oficial do CNJ.
- Naturezas: cível, penal e infracional, coletadas conjuntamente e classificadas separadamente na etapa de transformação.
- Volume piloto: até 100 registros por ano na consulta principal.
- Repositório: GitHub privado, sem versionamento de credenciais, respostas brutas ou identificadores processuais.
- Arquitetura: o piloto terá a mesma estrutura lógica da carga final; limites de páginas e volume serão parâmetros removíveis.

## 3. Terminologia das camadas

- **Bronze:** respostas originais da API, corpos das consultas, manifestos e metadados de execução.
- **Silver:** validação e normalização futura em relações separadas para processos, assuntos, movimentos e complementos, além de classificações derivadas e flags de qualidade.
- **Gold:** enriquecimentos territoriais, indicadores e agregações destinados à análise e ao dashboard.

Este incremento implementará apenas a coleta Bronze e o relatório de viabilidade necessário para projetar a Silver.

## 4. Estratégia de seleção temática

A consulta principal usará um catálogo versionado dos assuntos que o glossário oficial do programa Justiça pela Paz em Casa considera na definição de processos de violência doméstica. A versão oficial consultada na elaboração deste desenho inclui os códigos:

`10948`, `10949`, `11979`, `12194`, `12196`, `14097`, `14098`, `14226`, `14227`, `14228`, `14229`, `14942`, `14943`, `14944` e `14945`.

O catálogo armazenará, para cada código:

- tipo TPU;
- descrição oficial;
- natureza cível, penal ou infracional;
- fonte e data de consulta;
- vigência conhecida;
- justificativa de inclusão;
- versão do catálogo.

O código não tratará a lista como constante interna. Alterações no catálogo deverão gerar uma nova versão e permanecer rastreáveis no manifesto da coleta.

Uma consulta diagnóstica independente examinará registros associados a classes oficiais de medidas protetivas, inicialmente `1268` e `12423`, que não contenham assuntos do catálogo principal. Seus resultados ficarão isolados e não serão incorporados automaticamente ao conjunto PVD. A expansão da regra temática dependerá do relatório do piloto e de justificativa metodológica.

## 5. Consulta e particionamento

Cada ano será uma partição independente. A consulta principal combinará:

- intervalo anual em `dataAjuizamento`, fechado no início e aberto no início do ano seguinte;
- primeiro grau;
- presença de pelo menos um código do catálogo em `assuntos.codigo`;
- `size` configurável, igual a 100 no piloto;
- ordenação crescente e estável por `id.keyword`;
- `search_after` quando houver mais de uma página autorizada pela configuração.

O corpo exato da consulta será validado contra a API real, pois os sufixos de campos indexados podem variar em relação ao glossário conceitual. Ajustes de compatibilidade não poderão alterar silenciosamente o significado dos filtros.

A primeira coleta solicitará o `_source` completo. O objetivo é identificar a estrutura efetivamente retornada antes de adotar projeções de campos. Metadados externos a `_source`, incluindo `_id`, `_index`, `sort`, total de hits, relação do total, tempo, timeout e shards, também serão preservados.

## 6. Arquitetura de componentes

```text
src/datajud_tcc/
├── config.py       # leitura e validação da configuração
├── catalog.py      # catálogo temático versionado
├── query.py        # construção determinística das consultas
├── client.py       # HTTP, autenticação, timeout e retentativas
├── collector.py    # partições, paginação, checkpoints e coordenação
├── bronze.py       # persistência imutável e compressão
├── metadata.py     # manifestos, hashes e métricas
└── cli.py          # interface de linha de comando
```

As unidades terão interfaces pequenas e não dependerão das implementações internas umas das outras. A configuração definirá endpoint, anos, grau, catálogo, tamanho da página, limite de páginas, timeouts, esperas e diretórios.

Prefect, PostgreSQL e PostGIS não farão parte deste incremento. O coletor não dependerá desses componentes, o que permitirá adicioná-los posteriormente sem reescrever a aquisição e a persistência Bronze.

## 7. Estrutura de arquivos

```text
config/
├── collection.example.yaml
└── catalogs/pvd_cnj_<versao>.yaml
schemas/
├── bronze-response.schema.json
└── run-manifest.schema.json
tests/
├── unit/
├── integration/
└── fixtures/
work/
├── bronze/
├── checkpoints/
└── logs/
outputs/pilot/
```

Respostas reais serão armazenadas da seguinte forma:

```text
work/bronze/datajud/tjpr/
└── collected_at=AAAA-MM-DD/
    └── run_id=<identificador>/
        ├── manifest.json
        ├── requests/year=AAAA/page=NNNNNN.request.json
        └── responses/year=AAAA/page=NNNNNN.response.json.gz
```

`work/bronze`, checkpoints, logs potencialmente identificáveis, `.env` e demais segredos serão ignorados pelo Git. Fixtures de teste serão sintéticas. Relatórios em `outputs/pilot` conterão somente dados agregados e não identificáveis.

## 8. Contrato de execução e rastreabilidade

Cada execução receberá um `run_id` exclusivo e nunca sobrescreverá silenciosamente outra execução. O manifesto registrará:

- endpoint, tribunal, período, grau e versão do catálogo;
- hash da configuração efetiva;
- início, término e situação da execução;
- estado de cada partição anual;
- páginas e quantidade de registros recebidos;
- cursor inicial e final;
- códigos HTTP, tentativas e duração;
- `hits.total.value` e `hits.total.relation`;
- `timed_out` e situação dos shards;
- nomes e hashes dos artefatos;
- versão do coletor e ambiente relevante para reprodução.

O corpo efetivamente enviado será registrado sem o cabeçalho de autorização. O valor da chave será lido de variável de ambiente. O arquivo experimental que contém credencial embutida será substituído durante a implementação, e a chave exposta deverá ser considerada inadequada para reutilização.

## 9. Persistência, retomada e deduplicação

Cada resposta válida será comprimida e escrita primeiro em arquivo temporário. A promoção para o nome definitivo será atômica quando suportada pelo sistema de arquivos. O checkpoint avançará somente depois da validação mínima, persistência e cálculo do hash.

Na retomada, o coletor consultará o manifesto e os hashes antes de reutilizar páginas concluídas. Páginas incompletas ou inconsistentes serão refeitas. A Bronze apenas detectará duplicação técnica por página, `_id` ou hash; não realizará deduplicação substantiva de processos.

O cursor `search_after` será obtido exclusivamente do último hit persistido da página válida. Página vazia encerra a partição. O limite `max_pages_per_partition: 1` caracterizará o piloto; sua remoção ativará o mesmo fluxo paginado para a carga completa.

## 10. Erros e respostas inválidas

O cliente aplicará timeout separado de conexão e leitura, número máximo de tentativas e espera exponencial limitada. Em HTTP 429, respeitará `Retry-After` quando presente. Não haverá rotação de identidade nem concorrência agressiva para contornar limites.

Uma resposta HTTP 200 não será considerada válida se:

- não for JSON;
- não contiver a estrutura `hits.hits` esperada;
- indicar timeout;
- apresentar falhas de shards que comprometam a integridade da página;
- não fornecer valores de ordenação necessários à continuação quando houver próxima página.

Erros serão registrados sem credenciais ou conteúdo desnecessariamente identificável. A partição ficará com estado explícito de falha e não avançará silenciosamente.

## 11. Testes

### Testes unitários

- intervalos anuais e ausência de sobreposição;
- construção determinística das consultas;
- leitura e validação do catálogo;
- sanitização de cabeçalhos;
- convenção de caminhos e nomes;
- hashes e manifestos;
- interpretação do total e de sua relação;
- cálculo de espera e política de retentativas.

### Integração simulada

Fixtures sintéticas cobrirão página válida, página vazia, múltiplas páginas, HTTP 429, erro transitório, timeout, JSON inválido, falha de shard, interrupção e retomada. A retomada deverá provar que páginas já confirmadas não são duplicadas.

### Integração real controlada

A execução real fará uma página de até 100 registros em cada partição anual de 2019 a 2025, além da consulta diagnóstica limitada. Ela dependerá de credencial fornecida por variável de ambiente e não fará parte da suíte automática comum.

## 12. Relatório do piloto

O relatório agregará, por ano:

- estado da consulta;
- quantidade retornada;
- total informado e relação (`eq` ou `gte`);
- campos encontrados e percentuais de preenchimento;
- distribuição por assunto e classe;
- distribuição por natureza derivada, permitindo múltiplas naturezas por processo;
- duplicações técnicas observadas;
- cobertura de localização e datas;
- disponibilidade de movimentos e complementos;
- falhas, retries e alertas de estrutura.

O documento distinguirá resultados observados, hipóteses e limitações. Não converterá processos em vítimas ou ocorrências, não tratará município do órgão julgador como local do fato e não produzirá inferência estatística a partir dos 100 primeiros registros ordenados de cada ano.

## 13. Critérios de conclusão

O piloto estará tecnicamente concluído quando houver evidência de:

1. autenticação e resposta válida do endpoint do TJPR, ou documentação explícita de indisponibilidade após tentativas limitadas;
2. consultas anuais reproduzíveis;
3. preservação integral e verificável das respostas recebidas;
4. retomada sem duplicação após interrupção simulada;
5. ausência de segredos nos artefatos;
6. inventário do esquema realmente observado;
7. métricas de preenchimento e cobertura por ano;
8. relatório que recomende manter ou revisar catálogo, filtros, particionamento e estratégia de carga completa.

Sucesso dos testes simulados comprova o comportamento do software, mas não comprova acesso, cobertura ou qualidade da fonte. Não serão definidos limiares empíricos de aceitação antes da observação do piloto.

## 14. Fora do escopo deste incremento

- coleta integral dos sete anos;
- normalização Silver e banco PostgreSQL;
- enriquecimento territorial e PostGIS;
- orquestração com Prefect;
- dashboard;
- definição definitiva de indicadores de tempo entre movimentos;
- publicação de respostas brutas ou identificadores;
- conclusões sobre incidência, vítimas, ocorrências ou eficácia de políticas públicas.

## 15. Fontes metodológicas principais

- CNJ, API Pública do Datajud — glossário de campos: <https://datajud-wiki.cnj.jus.br/api-publica/glossario/>
- CNJ, API Pública do Datajud — endpoint, acesso e exemplos: <https://datajud-wiki.cnj.jus.br/api-publica/>
- CNJ, glossário Justiça pela Paz em Casa, versão consultada em 22/09/2026: <https://www.cnj.jus.br/wp-content/uploads/2025/12/glossario-anexo-semana-da-justica-pela-paz-em-casa.pdf>
- CNJ, Tabelas Processuais Unificadas: <https://www.cnj.jus.br/tabela-processuais-unificadas/>

