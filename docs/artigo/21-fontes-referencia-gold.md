# Fontes de referência para a Gold

Data: 07/11/2026. Status: **verificado** (fontes consultadas nesta data), exceto onde estiver marcado como lacuna. Responde às pendências de fonte do `20` §6. Evidências em `evidencias/referencias_gold_20261107/`. Script: `evidencias/scripts/referencias_gold.py`.

## 1. Território e população (IBGE)

| Item | Fonte | Resultado |
|---|---|---|
| Municípios do PR com mesorregião e região intermediária | API de Localidades do IBGE, `servicodados.ibge.gov.br/api/v1/localidades/estados/41/municipios` (consulta em 07/11/2026). Salvo em `ibge_municipios_pr_dtb.json` | 399 municípios e **10 mesorregiões** |
| População feminina por município | IBGE/SIDRA, **tabela 9514** (Censo Demográfico 2022: população residente por sexo, idade e forma de declaração da idade), variável 93, sexo = Mulheres, idade = Total. Salvo em `sidra_9514_pop_fem_pr_2022.json` | 399 municípios; **5.867.030 mulheres no PR** |
| Série anual por sexo? | IBGE/SIDRA, tabela 6579 (estimativas anuais): metadados sem classificação por sexo | **Não há** estimativa anual por sexo. Por isso o denominador é fixo, do Censo 2022, e a limitação é declarada (`20`, C2) |
| Tabela de referência consolidada | `ref_municipio_pr.json` (município → mesorregião, região intermediária, população feminina) | Pronta para virar `ref.municipio` na Gold |

**Mesorregiões, cobertura da base e população** (municípios-sede da Silver mapeados a partir de `registros_por_mesorregiao.json`; os 163 municípios-sede casam com a tabela do IBGE):

| Mesorregião | Municípios | Mulheres (Censo 2022) | Municípios-sede na base | Registros 2019–2026 |
|---|---:|---:|---:|---:|
| Metropolitana de Curitiba | 37 | 1.997.133 | 22 | 37.687 |
| Oeste Paranaense | 50 | 717.795 | 18 | 28.110 |
| Norte Central Paranaense | 79 | 1.174.040 | 30 | 27.322 |
| Sudoeste Paranaense | 37 | 289.928 | 13 | 12.339 |
| Centro Oriental Paranaense | 14 | 385.394 | 11 | 9.706 |
| Centro-Sul Paranaense | 29 | 277.002 | 10 | 8.647 |
| Norte Pioneiro Paranaense | 46 | 277.615 | 21 | 7.228 |
| Noroeste Paranaense | 61 | 370.697 | 18 | 7.143 |
| Centro Ocidental Paranaense | 25 | 174.731 | 10 | 5.225 |
| Sudeste Paranaense | 21 | 202.695 | 10 | 3.595 |

Todas as mesorregiões têm milhares de registros, o que confirma a decisão C1: o nível mesorregional é estável para mapas e taxas. A taxa bruta varia muito entre mesorregiões, e isso pode refletir diferenças de sigilo e de registro, não de judicialização. Comentário só descritivo; a análise fica para a Gold.

**Malha geográfica:** falta baixar a malha municipal do IBGE (SIRGAS 2000) para o PostGIS. Será a primeira tarefa territorial do plano da Gold, com a versão registrada.

## 2. Marcos legais (quebras de série)

Textos consultados no Planalto em 07/11/2026.

| Lei | Data / vigência | O que muda (relevante para a série) |
|---|---|---|
| **Lei nº 14.132/2021** ([texto](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14132.htm)) | 31/03/2021; vigência na publicação (DOU de 01/04/2021) | Cria o art. 147-A do Código Penal (**perseguição**), com pena aumentada de metade quando o crime é cometido contra mulher por razões da condição do sexo feminino, e revoga o art. 65 da Lei das Contravenções Penais |
| **Lei nº 14.188/2021** ([texto](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14188.htm)) | 28/07/2021; vigência na publicação (DOU de 29/07/2021) | Cria o art. 147-B do CP (**violência psicológica contra a mulher**), inclui o §13 no art. 129 (**lesão contra a mulher** por razões da condição do sexo feminino) e define o programa Sinal Vermelho |
| **Lei nº 14.994/2024** ([texto](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2024/lei/l14994.htm)) | 09/10/2024; vigência na publicação (DOU de 10/10/2024) | Torna o **feminicídio crime autônomo** (art. 121-A do CP, reclusão de 20 a 40 anos), aumenta a pena do art. 129, §13, e do **descumprimento de MPU** (art. 24-A da Lei Maria da Penha: reclusão de 2 a 5 anos) e dá prioridade de tramitação aos processos de violência contra a mulher (art. 394-A do CPP) |

Esses marcos explicam o surgimento ou a mudança de códigos da TPU no período: 14943 é a lesão em razão da condição de mulher (`07` §8), e as datas das leis devem ser comparadas com a primeira ocorrência de cada código na Silver. Vão para `ref_quebras_serie`, junto com a transição de códigos da TPU de 2021 (`07` §8) e as anomalias de registro de 2019–2020 (`08` §7).

## 3. Órgãos especializados (violência doméstica)

**Fonte oficial encontrada:** *Guia Institucional da CEVID-TJPR* (Paraná, 2021), [PDF no site do TJPR](https://www.tjpr.jus.br/documents/12054912/55371701/A+CEVID+-+Guia.pdf/e71d365b-cca7-bc5a-9ddf-deee4a18cdfb). O guia informa **10 juizados**: 3 em Curitiba, 2 em Londrina e 1 em cada uma das comarcas de Cascavel, Maringá, Ponta Grossa, Foz do Iguaçu e São José dos Pinhais. Segundo o guia, apenas os de Curitiba têm competência exclusiva para a Lei Maria da Penha; os demais acumulam crimes contra crianças, adolescentes e idosos.

**Na Silver** (`orgaos_especializados_silver.json`), aparecem órgãos especializados com **12 códigos** em **7 municípios-sede**: Curitiba (4 juizados, incluindo o 4º, posterior ao guia), Londrina (2), Ponta Grossa (2), Cascavel, Maringá, Foz do Iguaçu e São José dos Pinhais. Os nomes mudam no tempo para o mesmo código (por exemplo, "Juizado" passa a "1º Juizado" em Londrina, e aparece "2º Juizado" em Cascavel em 2025).

**Lacuna:** não foi encontrado ato oficial com as **datas de instalação** dos juizados criados depois de 2021, nem lista oficial atualizada. Notícias citam 13 varas, mas não entram como fonte. Consequências:
- a flag `especializado` fica **por código do órgão**, a partir do nome oficial do órgão na própria API, e é conferida com o guia de 2021;
- a capa traz o **órgão atual**, então a comparação da Q12 é entre processos **hoje** em órgão especializado ou comum (CLAUDE.md §4.6), não a situação na data do ajuizamento;
- se o autor obtiver no TJPR ou na CEVID a lista com datas, a vigência pode ser adicionada.

## 4. Validação externa

| Fonte | Situação |
|---|---|
| Painel de Violência contra a Mulher do CNJ, lançado em 2025 | **Feito** (extração manual do autor, 07/11/2026): ver `22`. Painel interativo com casos novos, pendentes e julgados por tribunal e unidade. **Extração manual** pelo autor: filtro TJPR, 1º grau, anos 2019–2025; registrar data de consulta e valores |
| Tabela do CNJ de 2019 por estado ([PDF](https://www.cnj.jus.br/wp-content/uploads/2020/03/Tabela-Processos-Resultados-Painel-2019-por-Estado-09032020.pdf)) | O acesso automático retornou HTTP 403; **baixar manualmente** |
| CNJ (2022), relatório sobre MPUs | Já resumido no `12`: números do TJPR em jan/2020–mai/2022 (sigilo, deferimento, tempo) |

As comparações devem explicar as divergências (universo público × total, classes, data de corte), sem buscar igualdade (`19` §7).

## 5. Códigos TPU: tipos, categorias e fases (proposta)

**Levantamento** (`codigos_silver_sgt.json`, 07/11/2026): todos os códigos da base de 147.002 registros, com nome e hierarquia oficiais do webservice SGT/CNJ:
- 67 classes;
- 347 assuntos;
- 180 movimentos (os presentes em pelo menos 20 registros).

Uma consulta falhou (movimento 391, HTTP 502 do SGT); a hierarquia dele já está em `evidencias/movimentos_viabilidade_20261023/`. Propostas abaixo, **a aprovar pelo autor** antes da Gold.

### 5.1 `ref_classe_tipo` (por hierarquia da TPU)

Arquivo: `proposta_ref_classe_tipo.json`. Cobre 100% das 67 classes. Regra: a posição da classe na árvore da TPU.

| Tipo | Regra na TPU | Registros | Principais classes |
|---|---|---:|---|
| `ACAO_PENAL` | Procedimento Comum; Processo Especial criminal | 60.609 | 10943, 283, 282 (Júri, com flag), 10944, 288 |
| `INQUERITO` | Procedimentos Investigatórios | 25.656 | 279, 280, 272, 278 (termo circunstanciado), 1733 |
| `CARTA` | Cartas (fora da série de entrada) | 22.242 | 355, 335 |
| `MPU` | 1268 | 19.363 | 1268 |
| `CAUTELAR_INCIDENTE` | Medidas Cautelares, Garantidoras, Preparatórias; Questões e Processos Incidentes; Petição Criminal | 18.174 | 305, 1727, 333, 306, 313 |
| `RECURSO` | Recursos (existem em 1º grau, por exemplo recurso em sentido estrito) | 255 | 426, 418 |
| `EXECUCAO` | Execução Penal e de Medidas Alternativas | 20 | 12729, 12727 |
| `OUTROS` | Administrativas, cíveis e inválida (`-1`) | 683 (0,5%) | 1199, 7, -1 |

Ajuste manual: a classe 11037 (Ação Penal Militar, 1 registro) cai em `CAUTELAR_INCIDENTE` pela regra e deve ir para `OUTROS`.

### 5.2 `ref_assunto_categoria` (multirrótulo, só para registros já selecionados pelo catálogo)

**Decisão do autor (07/11/2026):** aceitas a categoria **moral** (10ª) e a ligação de **12354 perturbação da tranquilidade** como antecessora de perseguição.

A Lei Maria da Penha (art. 7º) define cinco formas de violência doméstica: física, psicológica, sexual, patrimonial e moral. As categorias do `20` (C5) seguem essas formas e incluem "moral" (crimes contra a honra), que **não estava na lista do `19`**. Ela aparece em mais de 7 mil registros, então **proponho acrescentá-la (10ª categoria)**. Os códigos de ato infracional (`DIREITO DA CRIANÇA E DO ADOLESCENTE`) entram na categoria equivalente, com flag `infracional`.

| Categoria | Assuntos (registros na base) |
|---|---|
| Física (lesão) | 12194 (51.550), 14943 (14.571), 12196, 14945, 3386, 5556, 5557, 11238, 11237, 10842, 9642, **12345 vias de fato** (9.408). Na série ampliada: 5560 (13.994), 9647 |
| Psicológica | 14942 (2.029), 14944 |
| Ameaça | 3402 (42.789), 9661, 11253 |
| Perseguição | 14684 (1.742), 14686. Antecessor: **12354 perturbação da tranquilidade** (407), contravenção do art. 65 da LCP revogada pela Lei 14.132/2021; serve para ler a quebra de série |
| Sexual | Árvore "Crimes contra a Dignidade Sexual": 3465 estupro (93), 11417 (70), 12397 (66), 3466, 12398, 3468, entre outros. **Volume baixo** (algumas centenas) |
| Patrimonial | Árvore "Crimes contra o Patrimônio": 3426 dano (2.274), 5571 (547), 3416 (478), 3420, 3417, 3419, 3436, 3431, 5566, 3435, 9685. **Exceto** 14698 (dano contra a Administração Pública) |
| Moral (honra) | Árvore "Crimes contra a Honra": 12544 (7.319), 3397 (2.113), 3396, 3395, 12542, 12543, 9658 |
| Descumprimento de MPU | 14227 (14.243), 14229. **Não** 15180 (Lei Henry Borel, criança) |
| Feminicídio | 12091 (3.648); flag `tentado` quando há co-assunto 5555 |
| VD sem especificação | Registros só com os genéricos 10949, 11979, 10948 |

Os demais co-assuntos (violação de domicílio, cárcere privado, resistência, desacato, armas etc.) não recebem categoria e ficam como contexto. A taxa de "não classificados" será medida na Gold; o critério do `19` é menos de 2%.

### 5.3 `ref_movimento_fase` (por código e hierarquia)

| Fase / subtipo | Códigos |
|---|---|
| `DISTRIBUICAO` | 26 (`REDISTRIBUICAO`: 36, 12646, 12255) |
| `DECISAO_MPU`: deferimento / parcial / indeferimento | 11423 / 11424 / 11425 |
| `MPU_REVOGACAO`, `MPU_PRORROGACAO` | 11426; 14733 (12476: homologação de MPU, nome truncado, a conferir) |
| `RECEBIMENTO_DENUNCIA` (queixa; aditamento) | 391 (393; 388) |
| `REJEICAO_DENUNCIA` | 402, 404 |
| `AUDIENCIA` (subtipos) | 12750 instrução e julgamento, 12749 instrução, 12742 custódia, **12745 art. 16 da Lei 11.340 (renúncia à representação)**, 12753, 12743, 12741, 12747, 15188, 12740, 12744, 12739, 12752; 313 sessão do Júri |
| `SENTENCA_CONDENATORIA` | 219 procedência, 221 procedência em parte |
| `SENTENCA_ABSOLUTORIA` | 220, 11876, 11877 |
| `EXTINCAO_PUNIBILIDADE` | 11879, 1042, 1046, 11411, 1047, 1050, 1043, 1044, 12735, 1049, 12028 |
| `PRESCRICAO` | 11878, 471 |
| `SENTENCA_OUTRA` (sem mérito) | 461, 460, 463, 459, 12459, 455, 11376 |
| `PRONUNCIA` / `IMPRONUNCIA` (Júri) | 10953 / 10961 |
| `TRANSITO_JULGADO` | 848 |
| `ARQUIVAMENTO_INVESTIGACAO` (decisão) | 12430, 1063 |
| `ARQUIVAMENTO` definitivo (**marco terminal**) / provisório | 246 / 245 |
| `REATIVACAO` | 849, 893 |
| `CAUTELAR_PRISAO` (subtipos) | 175 homologação de flagrante, 12140 conversão em preventiva, 15032 manutenção, 128 revogação, 12141 relaxamento, 146 não homologação, 12148 domiciliar |
| `LIBERDADE_PROVISORIA` (concessão / não concessão) | 818 / 12146 |
| `SUSPENSAO` (SCP, revelia, ANPP) | 264, 12737; 263; 898; 12733 |
| `TRAMITACAO_DIRETA` | 14999, 15000 |
| `OUTRO` | demais (expediente, juntada, remessa, conclusão etc.) |

**`BAIXA`:** não há código de baixa entre os 180 movimentos levantados, o que confirma a decisão C7 (`20`).

**Observação para a análise:** a audiência do art. 16 da Lei Maria da Penha (12745, presente em 4.907 registros) é a audiência de renúncia à representação perante o juiz. Ela é um marco próprio do rito e pode ajudar a explicar parte das extinções por retratação ou renúncia.
