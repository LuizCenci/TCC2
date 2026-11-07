# Parâmetros da Gold, da análise final e dos dashboards

Data: 07/11/2026. Status: **decidido pelo autor (07/11/2026) nos pontos C1, C2, C5 e C6**; os demais são proposta. Este documento consolida o processo do `19` com as decisões já tomadas (`docs/superpowers/plans/2026-11-06-gold-insumos.md`), o CLAUDE.md e o TCC1. É a base do plano SDD da Gold.

**Decisões do autor (07/11/2026):**
- **C1 — Território: só mesorregião** (IBGE), atribuída pelo município-sede do órgão. Não há nível de comarca na Gold nem no dashboard. Onde o `19` diz "comarca", entende-se mesorregião.
- **C2 — Taxa:** "processos públicos por 100 mil mulheres" **por mesorregião**, com denominador da soma dos municípios (população feminina do Censo 2022), suavização Bayes empírica e aviso de cobertura.
- **C5 — Categorias:** união das listas, mais **moral** (decisão de 07/11, `21` §5.2). São **10 categorias** multirrótulo, seguindo as formas do art. 7º da Lei 11.340/2006, aplicadas só a registros já selecionados pelo catálogo. A perturbação da tranquilidade (12354) entra como antecessora de perseguição.
- **C6 — Supressão:** mínimo de **5 por mesorregião**; **10** em qualquer recorte mais fino (por exemplo, órgão julgador, ou especializada × ano × mesorregião). Aplicado no backend, com supressão secundária.

## 0. Eixo do trabalho (não muda)

O objetivo continua o do TCC1 e do CLAUDE.md §3: **produzir insights sobre a violência contra a mulher no Paraná a partir do Datajud, com um dataset consolidado e um dashboard**. Pelos limites do CLAUDE.md §4, isso se lê como **judicialização** (fluxo do sistema de Justiça), não como incidência da violência. O `19` não muda esse eixo, apenas o operacionaliza. O artigo mantém o contexto do TCC1 e só acrescenta o que decorre da execução.

Promessas do TCC1, cada uma com as perguntas da §3 que a atendem:

| Promessa do TCC1 | Onde é atendida |
|---|---|
| Diagnóstico espacial (georreferenciamento IBGE; por mesorregião, decisão C1) | Q01, Q02, Q12 |
| Características das agressões | Q03 (como **enquadramento processual**, CLAUDE.md §7) |
| Tempo de resposta para concessão de medidas de urgência (por mesorregião, decisão C1) | Q05 |
| Dataset consolidado e atualizável | Gold + Q15 |
| Dashboard de apoio ao planejamento público | §5 |

---

## 1. O que se mantém das decisões anteriores

- **Versão de cada registro:** a mais recente. `data_corte` é por registro (`concluida_em` da execução de origem), e o artigo usa um snapshot datado. Isso é compatível com `data_corte` do `19` §5.1.
- **Séries:** **estrita** (núcleo + específicas) como principal e **ampliada** como sensibilidade.
- **Escopo:** só G1, 2019–2026, e 2026 parcial (comparações jan–ago ou anualizadas com o corte explícito).
- **MPU ↔ ação penal não são ligáveis** (`07` §3), em linha com o `19` §2.2.
- **Repetições:** os 70 números de processo repetidos geram flag e uma sensibilidade que conta cada número uma vez.

---

## 2. Conflitos entre o `19` e as decisões anteriores: proposta de conciliação

| # | Tema | `19` diz | Antes | Proposta |
|---|---|---|---|---|
| C1 | Unidade geográfica | Comarca, com polígono e composição oficial com vigência | Mesorregião pelo município-sede; comarca opcional | **Dois níveis.** (a) **Comarca de sede** para tabelas, rankings e tempos: o município-sede do órgão identifica a comarca de sede, sem polígono e com *n* sempre visível. (b) **Mapa por mesorregião** como visão principal. O polígono por comarca (com `ST_Union` dos municípios) só entra se a **composição oficial do TJPR** for obtida (ato ou resolução, com vigência). Sem ela, não há mapa nem taxa por comarca |
| C2 | Taxa por 100 mil mulheres | Obrigatória em mapas | CLAUDE.md §11 proíbe dividir os processos da sede pela população do município e chamar de taxa de violência | Permitida **só com denominador da área atendida**: mesorregião (soma dos municípios) ou comarca com composição oficial. O rótulo é sempre "**processos públicos por 100 mil mulheres**", com suavização Bayes empírica e aviso de cobertura (só o acervo público; ≈5% das MPUs, `12`). **Denominador:** o IBGE publica população por sexo no **Censo 2022**, não nas estimativas anuais. Proposta: denominador fixo do Censo 2022, com essa limitação declarada. Conferir na fonte |
| C3 | Tipos de procedimento | MPU, INQUERITO, ACAO_PENAL, EXECUCAO, RECURSO, OUTROS | Principais / MPU / incidentes / cartas | A base é **só G1**: `RECURSO` não ocorre e `EXECUCAO` deve ser rara (conferir na Silver). Tipos propostos: `MPU` (1268); `INQUERITO` (279 e afins); `ACAO_PENAL` (10943, 283, 10944, com `282` Júri marcado por flag); `CAUTELAR_INCIDENTE` (305, 306, 313, 280, 333, 1727, 1199…); `CARTA` (355, 335; fora da série de entrada); `EXECUCAO` (se existir); `OUTROS`. `ref_classe_tipo` precisa cobrir 100% das classes da Silver |
| C4 | Deduplicação | `numeroProcesso + grau` | Flag + sensibilidade | Com só G1, a chave seria só o número. Manter **unidade = registro**, flag nos 70 e a sensibilidade "um por número". Escolher um registro canônico seria arbitrário sem saber a causa |
| C5 | Categorias | Física, psicológica, ameaça, perseguição, sexual, patrimonial, descumprimento, feminicídio, outros | 6 categorias (`07` §8) | **Unir:** lesão/física, psicológica, ameaça, perseguição, sexual, patrimonial, descumprimento de MPU, feminicídio, VD sem especificação. As categorias são aplicadas **apenas aos registros já selecionados pelo catálogo VCM**, usando também os co-assuntos (por exemplo 3402 Ameaça, 3426 Dano). Assim respeitam o CLAUDE.md §10: ameaça e dano não entram sozinhos como VCM, só qualificam um registro já incluído. Multirrótulo, sem soma. Os códigos de "sexual" e "patrimonial" precisam ser levantados na Silver e no SGT |
| C6 | Supressão de células | < 5 (avaliar até 10) | CLAUDE.md §13: avaliar | **10 por comarca e 5 por mesorregião**, aplicado no backend, com supressão secundária. Justificativa: comarcas pequenas e tema sensível |
| C7 | Marco `BAIXA` | Fase própria | `08` §2: não há código de baixa definitiva entre os 150 mais frequentes | O marco terminal é o **arquivamento definitivo (246)**. `BAIXA` só entra se um código for encontrado na Silver |
| C8 | Quebras de série | 2021 (perseguição, psicológica), 2024 (feminicídio autônomo), TPU | `07`/`08`: transição 5560 → 12194/14943 em 2021; anomalias de 2019–2020 | `ref_quebras_serie` com Lei 14.132/2021, Lei 14.188/2021 e Lei 14.994/2024 (conferir os textos oficiais), a transição de códigos da TPU (`07` §8) e as anomalias de registro de 2019–2020 (`08` §7) |

---

## 3. Catálogo de perguntas proposto

Abreviações:
- **AP** = ação penal; **INQ** = inquérito; **MPU** = medida protetiva.
- **KM** = Kaplan-Meier; **AJ** = Aalen-Johansen; **EB** = suavização Bayes empírica.

Toda pergunta é respondida na **série estrita**, com a **ampliada** como sensibilidade.

| id | Eixo | Pergunta | Métrica | Unidade | Tipo | Recortes | Método | Tabela Gold |
|---|---|---|---|---|---|---|---|---|
| Q01 | Volume | Como evolui a entrada de processos? | Novos processos por mês/ano de ajuizamento | registro | INQ, AP | ano, mês, mesorregião, categoria | Série temporal com quebras e 2026 marcado | `agg_volume` |
| Q02 | Volume | Onde a judicialização pública é proporcionalmente maior? | Processos públicos por 100 mil mulheres (bruta e EB) | registro | INQ, AP; MPU à parte | mesorregião | EB; Moran/LISA complementar | `agg_volume_territorio` |
| Q03 | Volume | Que enquadramentos predominam e como mudam? | % de processos com ao menos a categoria X | processo × categoria | INQ, AP, MPU | ano, mesorregião | Distribuição multirrótulo; UpSet | `agg_categoria` |
| Q04 | Proteção | Como as MPUs são decididas? | % concessão, parcial e não concessão (11423–11425) | MPU com decisão | MPU | ano, mesorregião, especializada | Proporções com *n* | `agg_mpu` |
| Q05 | Proteção | Quanto tempo leva a decisão da MPU? | Mediana KM (IC) e % decidido em até 2 dias (48 h) | MPU | MPU | ano, mesorregião, especializada | KM com censura | `agg_tempo` |
| Q06 | Proteção | Que medidas são concedidas? | Distribuição dos tipos de medida (complementos) | movimento de concessão | MPU | ano, mesorregião | Proporções; tendência | `agg_mpu_medida` |
| Q07 | Proteção | Com que frequência e em quanto tempo as MPUs são revogadas? | Incidência de revogação (11426) | MPU | MPU | ano, mesorregião | KM / AJ | `agg_mpu` |
| Q08 | Tempo | Quanto tempo até o recebimento da denúncia? | Mediana KM até 391 | processo | INQ/AP | ano, categoria, mesorregião | KM | `agg_tempo` |
| Q09 | Tempo | Quanto tempo até a sentença? | Mediana KM até o 1º julgamento (219/220/221…) | processo | AP | ano, categoria, mesorregião | KM | `agg_tempo` |
| Q10 | Desfecho | Como as ações terminam? | Incidência acumulada de condenação, absolvição, extinção, prescrição e arquivamento | processo | AP (INQ à parte para arquivamento) | coorte, categoria, mesorregião | AJ; prescrição em destaque | `agg_desfecho` |
| Q11 | Fluxo | Que caminhos os processos percorrem? | Variantes e tempo entre fases | evento | AP, INQ | mesorregião, especializada | Process mining (pm4py), sem `OUTRO` | `fato_evento` (agregado) |
| Q12 | Desigualdade | Órgãos especializados e comuns diferem? | Q05/Q09/Q10 por grupo, com contexto | processo | por tipo | especializada × comum | Comparação descritiva; sem linguagem causal | `agg_tempo`, `agg_desfecho` |
| Q13 | Proteção | Qual a resposta cautelar por enquadramento? | % com flagrante (175), preventiva (12140/15032), liberdade provisória (818) | processo | INQ, AP | categoria, ano | Proporções (proxy rotulado) | `agg_cautelar` |
| Q14 | Qualidade | Quão confiáveis e comparáveis são os dados? | Preenchimento, movimentos por processo por órgão (intensidade de registro), genéricos, datas inválidas, lacunas mensais, cobertura × CNJ | registro / órgão | todos | órgão, mesorregião, ano | Auditoria (`19` §3) | `qualidade_*` |
| Q15 | Arquitetura | O pipeline é reproduzível e atual? | Execuções, completude, SHA-256, duração, marca d'água, data de corte | execução | n/a | execução | Metadados de controle | `controle.*` (view) |

Regra do `19`: métrica fora do catálogo não entra no dashboard, e toda tabela Gold atende a pelo menos uma pergunta.

---

## 4. Parâmetros fixos propostos

| Parâmetro | Valor |
|---|---|
| Período | Ajuizamento 2019-01-01 a 2026-09-30; 2026 parcial |
| Coortes para desfecho | 2019–2021 como principal (mais de 90% com desfecho observado, `14`); demais com censura |
| Tempo | Dias desde `data_ajuizamento`, ignorando eventos anteriores ao ajuizamento (flag). Hipótese de fuso a verificar (`10` §9) |
| Censura | Sem marco terminal até `data_corte` do registro → `EM_ANDAMENTO`, `censurado = true` |
| *n* mínimo para estimar | KM/AJ por estrato só com *n* ≥ 30; abaixo disso, agregar ao nível superior |
| Não classificados | Menos de 2% dos registros sem categoria ou fase (`19` §10) |
| Supressão | Menos de 5 por mesorregião; menos de 10 em recortes mais finos; supressão secundária no backend |
| Territórios | IBGE DTB, mesorregiões (decisão C1); malha IBGE em SIRGAS 2000 (EPSG:4674), com `ST_Union` por mesorregião |
| Vara especializada | Lista oficial do TJPR, com vigência; a heurística por nome só serve de verificação |
| Linguagem | "processos judiciais", "medidas protetivas decididas"; nunca "casos de violência" |

---

## 5. Dashboards

As páginas propostas no `18` §4 continuam, agora rastreadas aos ids do catálogo:

| Página | Perguntas |
|---|---|
| Pipeline | Q15 |
| Cobertura e qualidade | Q14 |
| Temporal | Q01, Q03 |
| Território | Q02, Q12 |
| Medidas protetivas | Q04–Q07 |
| Trajetórias e desfechos | Q08–Q11, Q13 |
| Sensibilidade | estrita × ampliada, deduplicação, com ou sem 2019–2020 |

---

## 6. Pendências de fonte (não inventar)

1. ~~Composição das comarcas~~: dispensada (decisão C1).
2. Lista oficial das varas e juizados especializados, com vigência.
3. População feminina por município: Censo 2022 (IBGE), confirmando se há série anual por sexo.
4. Códigos TPU das categorias "sexual" e "patrimonial" e das fases (`ref_movimento_fase`), levantados na Silver e no SGT.
5. Textos das Leis 14.132/2021, 14.188/2021 e 14.994/2024, para `ref_quebras_serie`.
6. Painéis do CNJ, Justiça em Números e estatísticas do TJPR para a validação (`19` §7).
