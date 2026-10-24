# O que cada código do catálogo traz — exemplos, tipos de procedimento e ligação entre processos

Data: 23/10/2026. Fonte: Bronze `bronze-20261018-9852486`, registros ajuizados em **2019–2025** (132.495). Nenhuma consulta nova à API, exceto a busca de movimentos no SGT/CNJ (§5).

Status: §1–§6 são **achados verificados**; §7 é **recomendação de trabalho**, que depende de decisão do autor.

Evidências em `evidencias/exemplos_assuntos_20261023/`:

| Arquivo | Conteúdo |
|---|---|
| `exemplos_por_codigo.md` | 3 exemplos sorteados por código (semente 20261023), com classes e assuntos mais frequentes |
| `perfil_por_codigo.json` | Perfis numéricos por código |
| `perfil_classes_ligacao.json` | Tipo de classe × grupo; sinais de ligação entre processos |
| `movimentos_medida_protetiva.json` | Códigos dos movimentos de medida protetiva e tempos até o primeiro |

Scripts correspondentes em `evidencias/scripts/`.

**Privacidade dos exemplos:** não mostram número do processo nem `id`; as datas aparecem só como ano e mês; os movimentos aparecem como dias desde o ajuizamento.

## 1. Resumo por código

Registros de 2019–2025 que **contêm** o código. As contagens se sobrepõem, porque um registro pode ter vários assuntos.

| Código | Grupo | Registros | Classes mais frequentes | Aparece junto com |
|---|---|---:|---|---|
| 10949 VD contra a mulher (penal) | núcleo | 61.110 | Ação penal sumária, ação penal ordinária, inquérito | Ameaça (48%), 12194, 14943 |
| 12194 Lesão contra a mulher | núcleo | 48.008 | Ação penal sumária, ordinária, carta precatória | 10949, Ameaça |
| 1268 Medida protetiva (classe) | específica | 17.575 | — (é a própria classe) | 10949 (66%), Ameaça (50%), 12194 |
| 5560 Lesão decorrente de VD | ambígua | 13.993 | **Carta precatória (51%)**, inquérito, ação penal sumária | Ameaça, 10949, Injúria |
| 14227 Descumprimento de MPU | núcleo | 12.766 | Ação penal sumária, ordinária, liberdade provisória | 10949, Ameaça |
| 14943 Lesão em razão da condição de mulher | núcleo | 12.127 | Ação penal ordinária, inquérito, ação penal sumária | 10949, Ameaça |
| 11979 VD contra a mulher (infracional) | núcleo | 5.660 | Carta precatória (35%), ação penal sumária | Ameaça |
| 12091 Feminicídio | específica | 3.289 | **Liberdade provisória (25%)**, ação penal do Júri (24%), carta precatória | 10949, Crime tentado, Homicídio qualificado |
| 14942 Violência psicológica | núcleo | 1.646 | Medida protetiva (37%), ação penal ordinária, inquérito | 10949, Ameaça |
| 14684 Perseguição | secundária | 1.444 | Inquérito, ação penal ordinária, sumária | 10949 (45%), Ameaça |
| 12196 Lesão contra a mulher (infracional) | núcleo | 1.439 | Ação penal sumária, carta precatória | Ameaça, 10949 |
| 14686 Perseguição (infracional) | secundária | 256 | Medida protetiva, ação penal | 10949 |
| 14945, 14944, 9647, 14229, 10948, 14226 | vários | 1–135 | — | — |
| 14097, 14098, 14228, 12358, 15511, 15309, 12423 | — | **0** | — | — |

Observações:

- **10948 (cível):** tem só 20 registros, quase todos ações de **indenização por dano moral** ou material, além de alguns casos criminais classificados como cíveis. É marginal.
- **Infracionais (11979, 12196, 14944, 14945, 14686, 9647):** apesar do nome "ato infracional", aparecem majoritariamente em classes **criminais comuns** (ação penal, carta precatória, MPU) e em varas criminais. Isso sugere uso desses códigos fora do contexto de adolescente autor. É uma inconsistência de classificação a tratar na Silver.
- **Marcadores:** 12195 ("não identificadas como mulher") aparece junto com códigos específicos de mulher (14943, 12091), uma classificação contraditória. Os códigos 15174 e 15180 (Lei Henry Borel) chegam **sem nome** na API.
- **Assuntos aninhados:** cerca de 8 registros têm `assuntos` em estrutura aninhada (lista dentro de lista), como alertado no CLAUDE.md §7. Eles foram selecionados corretamente pela API, mas exigem normalização na Silver. Por isso as contagens por grupo da §2 diferem em até 8 registros das da `01-parametros-da-extracao.md` §5.

## 2. Achado central: cada código traz vários tipos de procedimento

Um mesmo fato de violência pode gerar vários **processos distintos** no TJPR: um inquérito, que depois vira ação penal no mesmo número (§3), um pedido de **medida protetiva** separado, **incidentes** (liberdade provisória, relaxamento de prisão, habeas corpus) e **cartas precatórias** para atos em outra comarca. Todos carregam os mesmos assuntos e entram no filtro.

Agrupamento de classes usado nesta análise (proposta, §7):

| Tipo | Classes |
|---|---|
| Principal | 279 Inquérito, 283 Ação penal ordinária, 10943 Sumária, 10944 Sumaríssima, 282 Júri, 278 Termo circunstanciado, 288, 272 |
| Medida protetiva | 1268 (e 15309, 12423, sem registros) |
| Incidente / cautelar | 305 Liberdade provisória, 306 Relaxamento de prisão, 307 Habeas corpus, 313 Prisão preventiva, 280 Auto de prisão em flagrante, 1727 Petição, 1199 Pedido de providências, 333 Insanidade mental e outras |
| Cooperação (cartas) | 355 Carta precatória, 335 Carta de ordem |
| Cível | 7, 156 |
| Outros | 426 Recurso em sentido estrito, 1291 Reabilitação e outras de baixa frequência |

Distribuição em 2019–2025:

| Grupo de inclusão | Principal | Medida protetiva | Incidente | Carta | Outros/cível | Total |
|---|---:|---:|---:|---:|---:|---:|
| Núcleo PVD | 72.796 (64%) | 14.652 (13%) | 12.596 (11%) | 13.928 (12%) | 511 | 114.483 |
| Específica sem PVD | 385 (7%) | 2.923 (54%) | 1.700 (32%) | 335 (6%) | 37 | 5.380 |
| Só ambígua (5560/9647) | 3.743 (31%) | — | 1.467 (12%) | **6.663 (56%)** | 24 | 11.897 |
| Só secundária | 493 (67%) | — | 191 (26%) | 31 (4%) | 20 | 735 |
| **Total** | **77.417 (58%)** | **17.575 (13%)** | **15.954 (12%)** | **20.957 (16%)** | 592 | **132.495** |

Implicações:

1. **Somar todos os registros não conta "casos".** Só cerca de 58% são procedimentos principais. O restante são procedimentos associados, que podem se referir ao mesmo fato.
2. **Cartas precatórias (16%) não são entrada de caso.** Elas pedem um ato (citação, audiência) a outro juízo; o caso tramita na origem, que pode ser outra comarca ou outro estado. No grupo ambíguo (5560) elas são a maioria (56%), o que reduz ainda mais o valor desse grupo como série de entrada.
3. **As extensões específicas trazem sobretudo medidas protetivas e incidentes.** Os feminicídios sem código PVD aparecem muito como liberdade provisória (pedido do réu preso), não só como ação penal do Júri.

## 3. É possível ligar processos do mesmo fato?

**Não, com os metadados públicos.** Verificado:

- O `_source` **não tem nenhum campo** de processo vinculado, de referência ou de origem. Os campos são `id`, `numeroProcesso`, `classe`, `assuntos`, `orgaoJulgador`, datas, `movimentos`, `sistema`, `formato`, `grau`, `nivelSigilo` e `tribunal`.
- O movimento **"Apensamento"** aparece 91.866 vezes, mas **nunca** traz complemento. Ele registra que houve apensamento, mas não a qual processo.
- O movimento **"Evolução da Classe Processual"** (65.048 ocorrências) traz complementos com siglas de tribunais (TJBA, TJCE, TJAM…), e não a classe anterior e a nova. Parece uma parametrização inconsistente, que não permite reconstruir a mudança de classe.
- 70 números de processo aparecem em mais de um registro, uma multiplicidade técnica a tratar na Silver.

O que **existe** de ligação é **dentro de um mesmo número**. Um inquérito que vira ação penal continua com o mesmo número e só muda de classe; a classe do registro é a **atual**. Assim, a contagem por classe mostra a fase atual de cada processo, e não a fase de entrada.

Tentar ligar processos por heurística (mesmo órgão, datas próximas, mesmos assuntos) seria pouco confiável e aumentaria o risco de reidentificação (CLAUDE.md §13). **Não recomendado.**

## 4. Unidade de análise resultante

A unidade analítica possível é o **procedimento judicial** (registro, deduplicado por número na Silver), classificado por **tipo de procedimento** e por **grupo de inclusão**. Não é possível contar "casos" ou "fatos" agregando procedimentos relacionados, nem, menos ainda, vítimas (CLAUDE.md §4.1).

## 5. Medidas protetivas: decisões identificáveis por código

No SGT/CNJ, o nome de movimento **"Medida protetiva" é compartilhado por quatro códigos** com sentidos opostos (`evidencias/sgt_tpu_20261018/movimentos_medida_protetiva.json`):

| Código | Caminho na TPU | Registros da classe 1268 com o movimento (de 17.575) | Dias do ajuizamento ao 1º movimento: mediana [P25–P75] |
|---:|---|---:|---|
| 11423 | Magistrado > Decisão > **Concessão** | 11.506 (65,5%) | 0 [0–1] |
| 11424 | Magistrado > Decisão > **Concessão em parte** | 1.650 (9,4%) | 0 [0–1] |
| 11425 | Magistrado > Decisão > **Não-Concessão** | 984 (5,6%) | 0 [0–3] |
| 11426 | Magistrado > Decisão > **Revogação** | 4.071 (23,2%) | 197 [52–414] |
| 14733 | Magistrado > Decisão > Prorrogação de Medida Protetiva | 1.279 (7,3%) | 246 [189–390] |

Implicações:

- **O código do movimento é obrigatório.** Classificar pelo nome trataria concessão, indeferimento e revogação como a mesma coisa (CLAUDE.md §4.8).
- **O indicador de tempo de resposta parece viável** para a classe 1268. A decisão inicial ocorre, na mediana, **no mesmo dia** do ajuizamento. Esse achado precisa de validação na Silver. Questões em aberto: (a) se ajuizamento equivale ao pedido nesta classe (CLAUDE.md §4.7); (b) registros sem nenhum movimento de decisão; (c) múltiplas decisões no mesmo registro; (d) a precisão das horas.
- Os **complementos** do movimento trazem **quais medidas** foram decididas (proibição de contato: cerca de 16 mil; de aproximação: cerca de 16 mil; afastamento do lar: cerca de 3,7 mil…) e o **beneficiário** ("A mulher" em cerca de 18 mil ocorrências, contra cerca de 300 para "A criança ou adolescente" e cerca de 160 para "O idoso"). O beneficiário pode servir para **confirmar** que a medida protege uma mulher, inclusive nos registros dos grupos ambíguo e secundário.

## 6. Resposta à pergunta "dá para usar todos os assuntos?"

**Sim, desde que não sejam somados como se fossem a mesma coisa.** Os registros não se conectam entre processos (§3), mas se organizam bem em duas dimensões que já existem nos dados:

1. **Grupo de inclusão** (núcleo, específica, ambígua, secundária): sustenta a série **estrita** (núcleo + específicas) e a **ampliada** (+ ambígua e secundária), como análise de sensibilidade.
2. **Tipo de procedimento** (principal, medida protetiva, incidente, carta, outros): define **o que** cada indicador conta.

## 7. Recomendação de trabalho (a decidir pelo autor)

1. **Série principal de judicialização:** procedimentos do tipo *principal* (inquérito, ações penais, Júri, termo circunstanciado), por ano/mês de ajuizamento, nas versões estrita e ampliada.
2. **Série de medidas protetivas:** classe 1268, com decisão inicial identificada pelo **código** do movimento (11423/11424/11425) e beneficiário "A mulher" quando disponível.
3. **Incidentes:** reportar à parte, como indicador de atividade processual, sem somar à entrada de casos.
4. **Cartas precatórias:** **excluir** das séries de entrada, mantendo-as na base com flag. Elas indicam cooperação entre juízos, não casos novos no PR.
5. **Grupo ambíguo (5560/9647):** só na série ampliada. Por ser majoritariamente carta precatória, o ganho real é menor do que os 11.897 registros sugerem: são 3.743 procedimentos principais.
6. **Infracionais e marcadores:** manter, com flags de inconsistência (códigos infracionais em classes criminais; 12195 junto com códigos de mulher), e medir a sensibilidade dos resultados à exclusão desses registros.
7. **Não ligar processos entre si.** Declarar no artigo que a unidade é o procedimento e que um mesmo fato pode gerar vários procedimentos.

## 8. Misturar ou separar assuntos? — recomendação de trabalho (23/10/2026)

Status: **recomendação**. As categorias e a escolha entre série estrita e ampliada **dependem de decisão do autor**, de preferência validada com o orientador.

**Não analisar cada código isoladamente**, porque:

1. A codificação muda no período: 5560 até 2021; depois 12194/14943, este criado pela Lei 14.188/2021 (51 registros em 2019, 4.121 em 2025). Séries por código mostrariam quebras de codificação, não de judicialização.
2. Os registros têm 1,9 assunto em média, então séries por código contariam o mesmo procedimento várias vezes.
3. Sete códigos não têm registros e seis têm menos de 140.
4. O 10949 é genérico e, isolado, não informa o tipo de violência.

**Não somar todos os códigos**, porque a soma infla o total por sobreposição e esconde a heterogeneidade: a mediana de movimentos vai de 34 no feminicídio a 90 na lesão.

**Proposta em três níveis**, sempre com o procedimento como unidade e combinada com o tipo de procedimento (§2):

1. **Série geral:** o procedimento entra se tiver ao menos um código do conjunto, **contado uma vez**. Duas versões: estrita (núcleo + específicas) e ampliada (+ ambíguas e secundárias).
2. **Categorias analíticas** multirrótulo, que atravessam a transição de 2021:

   | Categoria | Códigos |
   |---|---|
   | Lesão corporal | 12194, 14943, 12196, 14945 (+ 5560, 9647 na versão ampliada) |
   | Descumprimento de MPU | 14227, 14229 |
   | Violência psicológica | 14942, 14944 |
   | Feminicídio | 12091 |
   | Perseguição | 14684, 14686 |
   | VD sem especificação | registros com apenas 10949, 11979 e/ou 10948 |

   As categorias se sobrepõem; devem ser apresentadas lado a lado ou como "com ao menos X", **nunca somadas**. Combinações frequentes, como lesão com ameaça, podem ser exibidas explicitamente.
3. **Códigos individuais** apenas para diagnóstico: transição de codificação, inconsistências e documentação do catálogo.
