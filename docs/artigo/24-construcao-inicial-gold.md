# Primeira construção da Gold

Data: 07/11/2026. Status: **verificado** (execução real de `datajud-tcc gold-construir`, versão de regras `gold-2026-11-07`, sobre a Silver carregada em `17`; contagens consultadas no banco). O PC foi mantido acordado com `scripts/manter_acordado.ps1`.

## 1. Execução

| Etapa | Duração |
|---|---|
| Esquema, referências e território | 0,2 s |
| Transformações (`sql/10`–`30`) | 24,0 s |
| Total do comando (inclui o resumo de qualidade) | 42 s |

## 2. Contagens e metas

| Item | Valor | Conferência |
|---|---:|---|
| Processos (`gold.fato_processo`) | 147.020 | Igual ao número de `api_id` distintos da Silver (`17` §2) |
| `removido_indice` | 18 | Igual aos 18 registros de 2026 que saíram do índice entre 18/10 e 05/11 (`13`) |
| `numero_repetido` | 140 | 70 números de processo × 2 registros (`07` §3) |
| Sem mesorregião | 0 | Todos os municípios-sede mapeados (`21` §1) |
| Tipo `OUTROS` | 0,47% | Meta do `19` §10: menos de 2% |
| Sem categoria | 0,36% | Meta: menos de 2% |
| Eventos (`gold.fato_evento`) | 1.184.727 | Só movimentos com fase mapeada; de 13,7 milhões na Silver |
| Linhas de categoria | 183.444 | Multirrótulo |
| Eventos antes do ajuizamento | 14 registros | Ignorados nos marcos |
| Processos reativados após arquivamento definitivo | 7.516 | Tratamento à parte nas análises de tempo (`23`) |
| Processos com movimento duplicado (mesmo código e data/hora) | 67.402 | Achado de qualidade de registro; avaliar na análise da intensidade de registro (Q14) |
| Códigos de movimento presentes sem fase | 71,5% dos códigos distintos | Esperado: expediente e juntadas ficam como `OUTRO` |

## 3. Distribuições (descritivas, sem interpretação)

**Tipo de procedimento.** Primeiro número: registros. Segundo: registros na série estrita.

| Tipo | Registros | Série estrita |
|---|---:|---:|
| Ação penal | 60.611 | 58.384 |
| Inquérito | 25.668 | 23.550 |
| Carta | 22.242 | 15.535 |
| MPU | 19.364 | 19.364 |
| Cautelar/incidente | 18.176 | 16.455 |
| Outros | 684 | 656 |
| Recurso | 255 | 240 |
| Execução | 20 | 17 |

**Categorias** (processos com ao menos a categoria; não somar):

| Categoria | Processos | Dos quais só na série ampliada |
|---|---:|---:|
| Física | 89.565 | 13.111 |
| Ameaça | 42.851 | — |
| Descumprimento de MPU | 14.326 | — |
| VD sem especificação | 13.750 | — |
| Moral | 10.473 | — |
| Patrimonial | 3.915 | — |
| Feminicídio | 3.648 | — |
| Perseguição | 2.453 | — |
| Psicológica | 2.127 | — |
| Sexual | 336 | — |

Feminicídio tentado: 259. Processos em órgão especializado (órgão atual): 45.681.

**Desfecho das ações penais** (todas as coortes; os processos recentes estão censurados):

| Desfecho | Processos |
|---|---:|
| Condenação | 25.795 |
| Em andamento | 13.429 |
| Absolvição | 10.103 |
| Extinção da punibilidade | 4.548 |
| Prescrição | 2.738 |
| Rejeição da denúncia | 1.727 |
| Encerrado sem desfecho identificado | 921 |
| Sem mérito | 906 |
| Arquivamento da investigação | 444 |

**Primeira decisão das MPUs:** deferimento 12.415; parcial 1.652; indeferimento 1.098; sem decisão por código 4.199.

## 4. Observações para o plano de métodos

1. **A variável `desfecho` só tem sentido nas ações penais e nos inquéritos.** Em MPU aparecem 726 "condenações", porque o código 219 (procedência) também é usado no julgamento da própria medida, e 10.470 "encerrados sem desfecho". Para MPU, os tempos e resultados devem usar `dt_decisao_mpu`, `resultado_mpu` e `dt_revogacao_mpu` (`23`, uso de `censurado`).
2. **Os 7.516 processos reativados** precisam de regra explícita na análise de sobrevivência (`23`).
3. **Os movimentos duplicados em 46% dos processos** reforçam o risco de confundir intensidade de registro com tratamento diferente entre órgãos (`19` §3, §11 item 3).
4. As distribuições acima não têm corte de período nem censura tratada. Os indicadores do artigo virão dos métodos (Kaplan-Meier, Aalen-Johansen, Bayes empírico) no plano seguinte.
