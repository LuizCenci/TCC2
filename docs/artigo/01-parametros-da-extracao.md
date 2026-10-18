# Parâmetros da extração — camada Bronze (Datajud/TJPR)

Documento de referência para a seção de metodologia do artigo. Registra **todo parâmetro usado na extração**, com valor, justificativa e evidência.

| Item | Valor |
|---|---|
| Versão do documento | 1.2 — 18/10/2026 (tamanho de página, teto e timeout ajustados; ver `03-desempenho-api-coleta.md`) |
| Catálogo temático | `config/catalogs/tjpr_vcm_2026-10-18.yaml` — versão `tjpr-vcm-2026-10-18`, SHA-256 `df83d3ab…2f245035` |
| Configuração da coleta | `config/collection.bronze.yaml` — SHA-256 `e33374d7…b29aee6b` |
| Código que monta a consulta | `src/datajud_tcc/query.py` (`build_main_query`, `_thematic_filter`) |
| Status | Parâmetros **decididos pelo autor** em 18/10/2026. Volumes **verificados** na API em 17–18/10/2026, antes da coleta. |

Os hashes completos estão na §10. Cada execução de coleta grava no seu `manifest.json` a versão e o hash do catálogo e da configuração, o que permite ligar qualquer registro da Bronze a este documento.

---

## 1. Fonte de dados

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Fonte | API Pública do Datajud (CNJ) | Fonte oficial de metadados processuais (CNJ, Res. 331/2020). |
| Endpoint | `POST https://api-publica.datajud.cnj.jus.br/api_publica_tjpr/_search` | Índice público do TJPR. |
| Autenticação | Cabeçalho `Authorization: APIKey <chave pública vigente>` | Chave pública divulgada pelo CNJ; mantida fora do repositório (`.env`). |
| Tribunal | TJPR | Recorte do TCC (Paraná). |
| Linguagem de consulta | Elasticsearch Query DSL | Interface oferecida pelo endpoint. |

## 2. Recorte temporal

| Parâmetro | Valor |
|---|---|
| Campo de data | `dataAjuizamento` |
| Formato do campo no índice | `YYYYMMDDHHMMSS` (14 dígitos), **diferente** do ISO 8601 do glossário oficial (ver `docs/anotações tcc.md`) |
| Partição | Um intervalo por ano civil, semiaberto: `gte YYYY0101000000`, `lt (YYYY+1)0101000000` |
| **Período coletado** | **2019–2026** |
| **Período analisado** | **2019–2025** |

**Exclusão de 2026 da análise — opção do autor.** O ano de 2026 é coletado e mantido na Bronze, mas fica **fora de todas as análises e indicadores** por decisão do autor, porque o ano estava incompleto na data da coleta (outubro de 2026). Essa exclusão não decorre de falha ou inconsistência nos dados.

**Por que começar em 2019:** entre 2015 e 2018 o volume de registros com assuntos de violência doméstica quadruplica (4.442 → 18.603, todos os graus). Isso é compatível com a adoção progressiva dos códigos da TPU, e não necessariamente com mais processos (hipótese). A partir de 2019 a série é mais estável (§8).

**Significado da data:** o ajuizamento é a data de entrada do processo no Judiciário. Não equivale à data do fato nem à data do pedido de medida protetiva (CLAUDE.md §4.7).

## 3. Grau de jurisdição

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Filtro | `term grau.keyword = "G1"` | Processos originários de 1º grau. |
| Excluídos | G2, JE, TR | G2 são recursos do mesmo caso em outra instância e duplicariam processos. JE (Juizado Especial) é afastado pela Lei Maria da Penha (art. 41), e seus registros (cerca de 100 por ano) indicam classificação atípica. TR é desprezível (4 registros). |

## 4. Critério temático

Um registro é selecionado quando atende **a pelo menos uma** das condições:

```text
assuntos.codigo ∈ {núcleo PVD ∪ extensões do tipo assunto}
OU
classe.codigo   ∈ {extensões do tipo classe}
```

O critério é aplicado a **todos** os assuntos do processo, não só ao principal. O grupo que justificou a inclusão é derivável do próprio registro e será gravado na Silver (campo `motivo_inclusao`, CLAUDE.md §11).

Os nomes e caminhos abaixo foram conferidos no webservice público do SGT/CNJ em 18/10/2026. Os volumes são registros G1 ajuizados entre 2019 e 2026 que **contêm** o código; como um registro pode conter vários códigos, as contagens **se sobrepõem** e não devem ser somadas.

### 4.1 Núcleo PVD — 15 assuntos

Fonte: glossário do programa *Justiça pela Paz em Casa* (CNJ), que define os processos de violência doméstica contra a mulher. Os 15 códigos estão mantidos sem alteração em relação a `pvd_cnj_2025-07-17.yaml`.

| Código | Nome (TPU) | Caminho na TPU | Natureza | Registros G1 2019–2026 |
|---:|---|---|---|---:|
| 10949 | Violência Doméstica Contra a Mulher | Direito Penal | penal | 67.532 |
| 12194 | Contra a Mulher | Direito Penal > Lesão Corporal > Decorrente de Violência Doméstica | penal | 50.606 |
| 14943 | Lesão Cometida em Razão da Condição de Mulher | Direito Penal > Lesão Corporal | penal | 13.934 |
| 14227 | Crime de Descumprimento de Medida Protetiva de Urgência | Direito Penal > Crimes Previstos na Legislação Extravagante > Crimes Previstos na Lei Maria da Penha | penal | 13.870 |
| 11979 | Violência Doméstica Contra a Mulher | Direito da Criança e do Adolescente > Ato Infracional | infracional | 5.693 |
| 14942 | Violência Psicológica contra a Mulher | Direito Penal > Crimes contra a liberdade pessoal | penal | 1.935 |
| 12196 | Contra a mulher | Direito da Criança e do Adolescente > Ato Infracional > Lesões Corporais > Decorrente de Violência Doméstica | infracional | 1.447 |
| 14945 | Análogo à Lesão Corporal em Razão da Condição de Mulher | Direito da Criança e do Adolescente > Ato Infracional > Lesões Corporais | infracional | 136 |
| 14944 | Análogo à Violência Psicológica contra a Mulher | Direito da Criança e do Adolescente > Ato Infracional > Contra a liberdade pessoal | infracional | 92 |
| 14229 | Descumprimento de Medida Protetiva de Urgência | Direito da Criança e do Adolescente > Ato Infracional > Previstos na Legislação Extravagante > Previstos na Lei Maria da Penha | infracional | 75 |
| 10948 | Violência Doméstica Contra a Mulher | Direito Civil > Família | cível | 28 |
| 14226 | Crimes Previstos na Lei Maria da Penha | Direito Penal > Crimes Previstos na Legislação Extravagante | penal | 1 |
| 14097 | Violência Doméstica e Familiar contra a Mulher | Direito Penal > Violência Doméstica Contra a Mulher | penal | 0 |
| 14098 | Crimes de Descumprimento de Medida Protetiva de Urgência | Direito Penal > Violência Doméstica Contra a Mulher | penal | 0 |
| 14228 | Previstos na Lei Maria da Penha | Direito da Criança e do Adolescente > Ato Infracional > Previstos na Legislação Extravagante | infracional | 0 |

Códigos com zero ou poucos registros no TJPR foram mantidos para preservar a correspondência com a definição oficial do CNJ.

### 4.2 Extensões específicas — definem por si violência contra a mulher

| Código | Tipo | Nome (TPU) | Caminho na TPU | Registros G1 2019–2026 | Justificativa |
|---:|---|---|---|---:|---|
| 1268 | classe | Medidas Protetivas de Urgência (Lei Maria da Penha) – Criminal | Processo Criminal > Medidas Cautelares | 18.870 | 3.239 registros (17%) **não** têm assunto PVD e seriam perdidos. |
| 12091 | assunto | Feminicídio | Direito Penal > Crimes contra a vida | 3.559 | 2.736 registros (77%) **não** têm assunto PVD. |
| 15309 | classe | Medidas Protetivas de Urgência (Lei Maria da Penha) – Cível | Processo Cível e do Trabalho > Outros Procedimentos | 0 | Completude; sem uso no TJPR em 17/10/2026. |
| 12423 | classe | Medidas Protetivas de Urgência (Lei Maria da Penha) – Infracional | Procedimentos de Infância e Juventude > Seção Infracional > Procedimentos Cautelares | 0 | Completude. |
| 12358 | assunto | Feminicídio (ato infracional) | Direito da Criança e do Adolescente > Ato Infracional > Contra a vida | 0 | Completude. |
| 15511 | assunto | Medidas Protetivas de Urgência (Lei Maria da Penha) – Cível | Direito Processual Civil e do Trabalho > Tutela Provisória | 0 | Completude. |

### 4.3 Extensões ambíguas — violência doméstica sem distinção do sexo da vítima

| Código | Nome (TPU) | Caminho na TPU | Registros G1 2019–2026 | Justificativa |
|---:|---|---|---:|---|
| 5560 | Decorrente de Violência Doméstica | Direito Penal > Lesão Corporal | 13.994 | **Código-pai** de 12194 (*Contra a Mulher*) e de 12195 (*Contra pessoas não identificadas como mulher*). Foi usado sozinho até 2021 e depois substituído pelos filhos. Sem ele, a série teria uma quebra artificial em 2019–2020 (§8). |
| 9647 | Decorrente de Violência Doméstica (ato infracional) | Direito da Criança e do Adolescente > Ato Infracional > Lesões Corporais | 93 | Equivalente infracional de 5560 (pai de 12196/12197). |

**Restrição de uso:** esses registros abrangem vítimas de qualquer sexo e familiares. Eles **não podem** ser contados como violência contra a mulher sem qualificação. Na Silver, entram numa categoria própria e numa **série ampliada**, apresentada como análise de sensibilidade ao lado da **série estrita** (núcleo + específicas).

### 4.4 Extensões secundárias — não específicas de gênero

| Código | Nome (TPU) | Caminho na TPU | Registros G1 2019–2026 | Justificativa |
|---:|---|---|---:|---|
| 14684 | Perseguição | Direito Penal > Crimes contra a liberdade pessoal | 1.640 | Art. 147-A do CP (Lei 14.132/2021). A pena é aumentada quando o crime é contra a mulher por razões da condição do sexo feminino. Inclusão analítica a decidir na Silver. |
| 14686 | Perseguição (art. 147-A, ato infracional) | Direito da Criança e do Adolescente > Ato Infracional > Contra a liberdade pessoal | 299 | Equivalente infracional. |

### 4.5 Marcadores para a Silver — coletados, mas fora do filtro

Esses códigos **não selecionam** registros. Quando aparecem num registro selecionado por outro critério, geram uma flag de qualidade na Silver.

| Código | Nome (TPU) | Registros no recorte | Uso previsto |
|---:|---|---:|---|
| 12195 | Contra pessoas não identificadas como mulher (filho de 5560) | 157 | Exclusão ou revisão: indica vítima que não é mulher. |
| 12197 | Contra pessoas não identificadas como mulher (filho de 9647) | 0 | Idem, infracional. |
| 15174 | Violência Doméstica e Familiar contra Criança e Adolescente | 112 | Revisão: possível vítima criança ou adolescente. |
| 15180 | Descumprimento de Medida Protetiva (Lei Henry Borel) | 51 | Revisão: medida protetiva de criança ou adolescente. |

### 4.6 Critérios avaliados e rejeitados

| Critério | Motivo da rejeição |
|---|---|
| Extrair todo o TJPR | 8,9 milhões de registros fora do catálogo (2019–2026, todos os graus). Volume desproporcional e sem utilidade para o tema; viola a orientação de não sobrecarregar a infraestrutura do CNJ. |
| Assuntos genéricos como filtro: 3402 Ameaça, 12345 Vias de fato, 3386 Lesão leve, 3465 Estupro, 11417 Estupro de vulnerável | Não específicos de gênero; trariam majoritariamente casos sem relação com o tema. Eles **continuam presentes** na Bronze como assuntos secundários dos processos selecionados. |
| Filtro por órgão julgador (Juizados de Violência Doméstica) | Só 7 cidades têm juizado especializado, e eles acumulam crimes contra crianças e idosos (13.520 processos G1 sem código PVD). Traria ruído e não cobriria o interior. |
| Classe 1268 como consulta diagnóstica separada (plano do piloto) | Incorporada ao filtro principal (§4.2). A consulta diagnóstica foi desativada nesta versão do catálogo. |
| Códigos sem relação com violência contra a mulher (13574/13761 "Afastamento Mulher – Lei Maria da Penha", 15142/15143 eleitorais) | Zero registros no TJPR ou outro ramo do Direito. |

## 5. Volume esperado — verificado antes da coleta

Contagem exata (`track_total_hits: true`, `relation: eq`) obtida com a **mesma consulta gerada pelo código do projeto**, trocando apenas `size` para 0, em 18/10/2026. Os grupos são **exclusivos**, com atribuição hierárquica: núcleo > específica > ambígua > secundária.

| Ano | Total | Núcleo PVD | Específica sem PVD | Só ambígua | Só secundária |
|---|---:|---:|---:|---:|---:|
| 2019 | 24.956 | 19.146 | 752 | 5.057 | 1 |
| 2020 | 24.766 | 17.595 | 885 | 6.282 | 4 |
| 2021 | 15.120 | 13.871 | 659 | 550 | 40 |
| 2022 | 14.492 | 13.690 | 719 | 3 | 80 |
| 2023 | 16.023 | 15.145 | 732 | 5 | 141 |
| 2024 | 17.631 | 16.687 | 738 | 0 | 206 |
| 2025 | 19.507 | 18.357 | 894 | 0 | 256 |
| **2019–2025 (analisado)** | **132.495** | **114.491** | **5.379** | **11.897** | **728** |
| 2026 (coletado, fora da análise) | 10.842 | 10.153 | 556 | 1 | 132 |
| **Total coletado** | **143.337** | **124.644** | **5.935** | **11.898** | **860** |

Os totais são do índice em 18/10/2026. Como o índice é atualizado continuamente, a contagem efetiva da coleta é registrada no manifesto de cada execução e pode diferir ligeiramente.

## 6. Paginação e completude

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Tamanho da página (`size`) | 200 | A API tem latência fixa de cerca de 22–33 s por consulta e o gateway corta consultas acima de 60 s (HTTP 504). Com 200 registros, a página leva cerca de 40 s (`03-desempenho-api-coleta.md`). |
| Ordenação | `id.keyword` ascendente | Chave única por registro: ordem determinística e sem empates. |
| Paginação | `search_after` com o `sort` do último registro | Método documentado pelo CNJ para percorrer além de 10.000 resultados. |
| Contagem | `track_total_hits: true` | Sem isso o Elasticsearch para em 10.000 (`relation: gte`). |
| Limite de páginas por ano | 300 | Teto de segurança. O maior ano tem cerca de 125 páginas; atingir o teto marca a partição como `limited`, nunca como completa. |
| Fim da partição | Página vazia ou com menos de `size` registros | — |
| Proteção contra laço | Erro se um cursor `search_after` se repetir | — |
| Campos retornados | `_source` completo, sem projeção | Preserva assuntos, movimentos e complementos para a Silver. |

**Limitação conhecida:** a paginação não usa *point-in-time*. Se o índice for atualizado durante a coleta, um registro pode ser omitido ou repetido. Mitigação: a completude de cada ano é verificada comparando os registros coletados com `hits.total`, e as duplicatas por `id` são tratadas na Silver.

## 7. Robustez e respeito à infraestrutura

| Parâmetro | Valor |
|---|---|
| Timeout de conexão / leitura | 10 s / 90 s (acima do corte de 60 s do gateway) |
| Tentativas por requisição | até 3 |
| HTTP 429 | Espera o `Retry-After` informado, limitado a 30 s |
| HTTP 502/503/504 e falhas de conexão | Recuo exponencial (1 s, 2 s…), limitado a 30 s |
| HTTP 401/403 | Interrompe; não insiste |
| Validação da resposta | Rejeita `timed_out = true`, `_shards.failed > 0`, `hits.total` inválido e registro sem `sort` |
| Em caso de falha num ano | Interrompe a coleta (`continue_on_partition_error: false`); a mesma execução é retomada do checkpoint, no máximo 5 vezes, com 2 min de pausa |
| Retomada | Checkpoint por ano no manifesto (último cursor); páginas já gravadas são verificadas por SHA-256 |
| Concorrência | Uma requisição por vez; nenhuma rotação de identidade |

## 8. Características dos dados observadas (relevantes para a interpretação)

1. **Mudança de codificação em 2021.** O assunto 5560 aparece sozinho em cerca de 5–6 mil registros por ano em 2019–2020 e desaparece em 2022. No mesmo período o 14943 (Lei 14.188/2021) passa de 51 registros (2019) para 4.121 (2025). Séries por assunto devem considerar essa transição.
2. **Queda em 2021–2022.** Mesmo com as extensões, o total cai de cerca de 25 mil (2019–2020) para cerca de 15 mil (2021). Hipóteses a investigar: pandemia, migração de sistema, mudança de codificação. Não deve ser interpretada como redução da violência.
3. **Sem processos sigilosos.** `nivelSigilo = 0` em 100% dos registros. O índice público não inclui processos em segredo de justiça, e isso é uma **limitação de cobertura**.
4. **Localização.** `orgaoJulgador.codigoMunicipioIBGE` está sempre preenchido, mas com só 163 municípios: as **sedes dos órgãos julgadores**, não o local do fato.
5. **Sistema e formato.** `sistema` é 99% "Eproc" inclusive em 2019 (reflete o sistema atual, não o de origem). `formato` é 100% eletrônico. Nenhum dos dois serve para estratificação histórica.
6. **Multiplicidade de assuntos.** São 1,9 assunto por registro em média (máximo 12), o que reforça a necessidade de tabelas separadas na Silver (CLAUDE.md §9).

## 9. Armazenamento na Bronze

- Uma requisição (`page=NNNNNN.request.json`) e uma resposta original comprimida (`page=NNNNNN.response.json.gz`) por página, organizadas por ano.
- Caminho: `work/bronze/datajud/tjpr/collected_at=<data>/run_id=<id>/`. Esse diretório não é versionado no git, por privacidade (CLAUDE.md §13).
- O `manifest.json` de cada execução registra endpoint, tribunal, grau, anos, versão e hash do catálogo, hash da configuração, versão do coletor, totais por ano, cursor, metadados das respostas (`took`, `timed_out`, `_shards.failed`) e o SHA-256 de cada página.
- Nenhum campo é descartado na Bronze. A redução e a anonimização ocorrem na Silver.

## 10. Reprodução

```text
Catálogo:     config/catalogs/tjpr_vcm_2026-10-18.yaml
              sha256 df83d3abad719b373da7b97b0e917432dcb1c5a292447d8519c69fef2f245035
Configuração: config/collection.bronze.yaml
              sha256 e33374d768f1e5db10b5330d2877597704fd9bac2088dc0e373e923bb29aee6b
Catálogo PVD original (inalterado): config/catalogs/pvd_cnj_2025-07-17.yaml
              sha256 d0a96c176c891d851360f0f08c291dfa6052f3e50249d9bd3825f2d0d29c72a5
```

```text
.\.venv\Scripts\datajud-tcc.exe collect --config config/collection.bronze.yaml
```

A consulta completa de exemplo (ano 2019) está em `evidencias/validacao_filtro_20261018/validacao_filtro.json`, campo `query_example_2019`.

## 11. Evidências

| Evidência | Local |
|---|---|
| Agregações exploratórias (consultas e respostas, sem documentos de processos) | `evidencias/datajud_agregacoes_20261017/` |
| Nomes, hierarquia e glossário da TPU (webservice SGT/CNJ) | `evidencias/sgt_tpu_20261018/` |
| Validação do filtro do código e volumes por grupo | `evidencias/validacao_filtro_20261018/` |
| Scripts das consultas | `evidencias/scripts/` |
| Análise exploratória que fundamentou as decisões | `02-analise-exploratoria-parametros.md` |
| Divergência do formato de `dataAjuizamento` | `../anotações tcc.md` |

## 12. Histórico de decisões

| Data | Decisão | Origem |
|---|---|---|
| 22/09/2026 | Núcleo PVD (15 assuntos) e classes 1268/12423 como diagnóstico | Desenho do piloto |
| 03/10/2026 | Formato `YYYYMMDDHHMMSS` para `dataAjuizamento` | Verificação empírica |
| 18/10/2026 | Filtro = núcleo + extensões (específicas, ambíguas, secundárias); só G1; coleta 2019–2026; **análise 2019–2025, com 2026 excluído por opção do autor**; sem partição diagnóstica por órgão | Decisão do autor, com base em `02-analise-exploratoria-parametros.md` |
| 18/10/2026 | `page_size` 100 → 1.000, teto 1.000 → 100 páginas/ano, timeout de leitura 60 → 180 s. Primeira execução (`bronze-20261018-24c258c`) interrompida após 26 páginas e descartada. Filtro inalterado. | Medição de desempenho, `03-desempenho-api-coleta.md` |
| 18/10/2026 | Execução com 1.000 por página (`bronze-20261018-12748ce`) falhou por HTTP 504 (corte de 60 s do gateway), sem páginas gravadas. Final: `page_size` 200, teto 300 páginas/ano, timeout 90 s, retomada automática limitada a 5 vezes. | `03-desempenho-api-coleta.md`, §4–5 |
