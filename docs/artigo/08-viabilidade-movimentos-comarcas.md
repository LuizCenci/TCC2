# Viabilidade de indicadores com movimentos e de agregação por comarca

Data: 23/10/2026. Fonte: Bronze `bronze-20261018-9852486`, registros ajuizados em 2019–2025 (132.495; 12.526.626 movimentos). Nenhuma consulta nova ao Datajud. A hierarquia dos movimentos foi obtida no SGT/CNJ.

Status: §1–§7 são **achados verificados**; as hipóteses estão marcadas como tais. §8 é **recomendação de trabalho**.

Evidências em `evidencias/movimentos_viabilidade_20261023/`:

| Arquivo | Conteúdo |
|---|---|
| `hierarquia_movimentos_sgt.json` | Hierarquia oficial dos 150 códigos de movimento mais frequentes |
| `viabilidade.json` | Eventos, Kaplan-Meier, movimentos e sedes |
| `anomalia_2019_2020.json` | Distribuição mensal 2019–2021 |
| `ano_numero_cnj.json` | Ano do número CNJ × ano de ajuizamento, só agregado |
| `classe_por_ano_inicio.json` | Classe por ano e primeiro movimento |

Scripts: `extrato_movimentos.py`, `sgt_hierarquia_movimentos.py`, `viabilidade_movimentos.py`, `anomalia_2019_2020.py`, `ano_numero_cnj.py`, `classe_por_ano_inicio.py`. O extrato intermediário, sem identificadores, fica em `work/analise/` e não é versionado.

Tipos de procedimento conforme `07-o-que-cada-assunto-traz.md`, §2. "Estrita" = núcleo PVD + extensões específicas.

## 1. Qualidade das datas dos movimentos

| Medida | Valor |
|---|---:|
| Movimentos | 12.526.626 |
| Sem `dataHora` | 0 |
| Anteriores ao ajuizamento | 24 |
| Códigos de movimento distintos | 269 |

As datas dos movimentos são utilizáveis. Os 24 casos anteriores ao ajuizamento são desprezíveis e são ignorados nos cálculos de tempo.

## 2. Eventos definidos pela hierarquia oficial (SGT/CNJ)

Os eventos foram definidos pelo **código** e pela posição na TPU, não pelo nome (lição da `07`, §5):

| Evento | Códigos | Caminho na TPU |
|---|---|---|
| **Arquivamento definitivo** (evento de fim) | 246 "Definitivo" | Serventuário > Escrivão > Arquivamento |
| Julgamento | 219, 220, 221, 455, 459–461, 463, 471, 1042–1044, 1046, 1047, 1049, 1050, 11411, 11876–11879, 12735 | Magistrado > Julgamento (193), **exceto** embargos de declaração (198, 200, 871), pronúncia (10953), provimento (237) e prejudicado (12459), que não encerram a instância |
| Trânsito em julgado | 848 | Serventuário > Escrivão |
| Reabertura | 849 Reativação, 893 Desarquivamento | Serventuário > Escrivão |

Não foi encontrado código de "baixa definitiva" entre os 150 movimentos mais frequentes. O arquivamento definitivo é o único evento de fim disponível de forma ampla.

## 3. Presença dos eventos (série estrita)

| Tipo | N | Arquivamento definitivo | Julgamento | Trânsito | Reabertura |
|---|---:|---:|---:|---:|---:|
| Principal | 73.187 | 67,2% | 65,5% | 64,5% | 5,5% |
| Medida protetiva | 17.575 | 92,9% | 16,3% | 4,3% | 11,0% |
| Incidente/cautelar | 14.296 | 94,0% | 2,6% | 4,0% | 7,2% |
| Carta precatória/ordem | 14.263 | 99,1% | 0,0% | 0,0% | 5,4% |

Registros só da série ampliada (principal: N = 4.230) têm 91,4% de arquivamento definitivo. Eles se concentram em 2019–2020, por isso tiveram mais tempo para encerrar.

## 4. Tempo até o arquivamento definitivo (Kaplan-Meier)

Procedimentos sem arquivamento definitivo são tratados como **censurados** na data da coleta (18/10/2026). A curva considera o primeiro arquivamento definitivo; as reaberturas (§3) são posteriores e não entram no cálculo.

**Por tipo** (2019–2025):

| Tipo | N | Encerrados | Mediana (dias) | Encerrados em 1 ano | 2 anos | 3 anos |
|---|---:|---:|---:|---:|---:|---:|
| Principal | 77.417 | 53.030 | **1.037** | 15,1% | 33,8% | 53,2% |
| Medida protetiva | 17.575 | 16.327 | 197 | 69,4% | 85,9% | 94,1% |
| Incidente/cautelar | 15.954 | 15.055 | 53 | 87,9% | 94,9% | 97,7% |
| Carta precatória/ordem | 20.957 | 20.831 | 63 | 89,8% | 97,9% | 99,6% |

**Procedimentos principais por ano de ajuizamento:**

| Ano | N | Mediana (dias) | 1 ano | 2 anos | 3 anos |
|---|---:|---:|---:|---:|---:|
| 2019 | 17.022 | 1.211 | 11,9% | 26,6% | 43,2% |
| 2020 | 10.723 | 1.065 | 13,9% | 31,0% | 52,0% |
| 2021 | 9.442 | 940 | 15,5% | 36,3% | 59,5% |
| 2022 | 8.795 | 848 | 19,1% | 42,0% | 64,5% |
| 2023 | 9.487 | 886 | 17,8% | 41,1% | 58,3%* |
| 2024 | 10.441 | não atingida | 18,6% | 38,0%* | — |
| 2025 | 11.507 | não atingida | 12,1%* | — | — |

\* Estimativas com acompanhamento incompleto: a coorte não teve tempo de chegar ao ponto, então os valores estão no limite da observação.

Leitura:

- O **tempo de tramitação é mensurável** com análise de sobrevivência. A média ou a mediana só dos encerrados seria enviesada. Em 2025, por exemplo, só 1.672 de 11.507 procedimentos estão encerrados.
- Para **medida protetiva**, o arquivamento (mediana de 197 dias) coincide com a mediana da **revogação** (197 dias, `07` §5). O intervalo aproxima o **tempo de vigência** da medida, não um "tempo de resposta". O tempo de resposta é a decisão inicial (mediana de 0 dias).
- **Cartas e incidentes** encerram rápido por natureza. Misturá-los com os principais distorceria qualquer tempo médio.
- As coortes recentes parecem encerrar mais rápido (mediana de 1.211 dias em 2019 contra 848 em 2022). Isso pode ser composição de classes (§7.3) ou mudança de prática; **não deve ser lido como ganho de eficiência** (CLAUDE.md §4.10).

## 5. Número de movimentos

| Tipo | Mediana | P25–P75 |
|---|---:|---|
| Principal | 130 | 68–183 |
| Medida protetiva | 49 | 35–72 |
| Incidente/cautelar | 28 | 24–40 |
| Carta precatória/ordem | 16 | 14–21 |

Os movimentos mais frequentes são administrativos: "Documento" (2,05 mi), "Expedição de documento" (1,55 mi), "Recebimento" (1,24 mi), "Ato ordinatório" (1,21 mi), "Confirmada" (1,01 mi, comunicação eletrônica). O **total de movimentos** mede sobretudo volume de expediente e varia com o tipo de procedimento e a prática da vara. Ele só serve como descritivo dentro do mesmo tipo, e não como medida de complexidade ou eficiência.

## 6. Agregação por comarca (sede do órgão julgador)

Procedimentos principais, 2019–2025:

| Medida | Valor |
|---|---:|
| Sedes distintas (`codigoMunicipioIBGE` do órgão) | 163 |
| Procedimentos por sede no período: mediana [P25–P75] | 201 [113–440] |
| Mínimo / máximo | 12 / 8.138 |
| Sedes com ≥ 30 procedimentos **em todos os anos** | 43 |
| Sedes com ≥ 100 no período | 127 |
| Sedes com ≥ 300 no período | 60 |
| Sedes com ≥ 50 encerramentos (para estimar tempo) | 144 |

Leitura:

- **Séries anuais por comarca** só são estáveis para cerca de **43 sedes**. A sede mediana tem cerca de 29 procedimentos principais por ano.
- **Indicadores do período inteiro por comarca** (volume, mediana de tempo) são viáveis para cerca de **127–144 sedes**, sempre com N e intervalo.
- Para comparações temporais e territoriais ao mesmo tempo, recomenda-se **agregar as comarcas em regiões**.
- A sede indica onde o processo **está hoje** (CLAUDE.md §4.6). Ainda é necessária a correspondência oficial comarca → municípios do TJPR (§4.5).

## 7. Fatores que afetam as séries temporais

### 7.1 Pico de cartas precatórias (jul/2019–dez/2020)

As cartas sobem de cerca de 100 por mês (início de 2019 e a partir de 2021) para **1.150–1.220 por mês em jan–mar/2020**. Em 2020, 5.067 das 9.605 cartas têm o assunto 5560, e elas se concentram nos Juizados de Violência Doméstica de Curitiba e Maringá. O pico começa antes da pandemia. **Causa não identificada** (hipótese: prática administrativa de expedição). É mais um motivo para excluir cartas das séries de entrada (`07` §7).

### 7.2 Procedimentos principais iniciados por "Documento" (2019–2020)

Em 2019 e 2020, respectivamente **5.048** e **3.854** procedimentos principais têm como primeiro movimento "Documento" (581), em vez de "Petição". Em 2021–2025 isso ocorre em 10 casos ou menos por ano. São sobretudo ações penais sumárias (atualmente).

- **Hipótese testada e descartada:** processos antigos migrados com nova data. Em **100%** dos registros, o ano do número CNJ é igual ao ano de `dataAjuizamento`.
- **Causa não identificada.** Esses registros explicam boa parte do volume maior de 2019 (17.022 principais, contra 8.795–11.507 nos anos seguintes). A série precisa ser apresentada com essa ressalva, e a sensibilidade deve ser testada com e sem esses registros.

### 7.3 Mudança de composição das classes

| Ano | Ação penal sumária | Ação penal ordinária | Inquérito |
|---|---:|---:|---:|
| 2019 | 59% | 12% | 27% |
| 2022 | 43% | 34% | 20% |
| 2025 | 20% | 39% | 39% |

1. **A classe é a fase atual.** Coortes recentes ainda estão mais em inquérito, simplesmente porque tiveram menos tempo para virar ação penal.
2. **Sumária → ordinária.** É compatível (hipótese) com a Lei 14.188/2021, que elevou a pena da lesão contra a mulher por razões da condição do sexo feminino (art. 129, §13, CP). Isso levaria ao rito ordinário.
3. **Tramitação direta MP–polícia (movimento 14999)** passa de 63–201 registros por ano (2019–2021) para **8.700–10.700 por ano (2023–2025)**. A prática processual mudou, o que afeta a contagem de movimentos e os tempos.

## 8. Conclusão de viabilidade e recomendação de trabalho

| Indicador | Viabilidade | Condições |
|---|---|---|
| Tempo até a decisão inicial da MPU | **Viável** | Códigos 11423/11424/11425; mediana de 0 dias (`07` §5) |
| Tempo de vigência da MPU (até revogação ou arquivamento) | **Viável** | Interpretar como vigência, não como resposta |
| Tempo de tramitação dos principais | **Viável, com sobrevivência** | Kaplan-Meier por coorte; mostrar % encerrado em 1/2/3 anos; não usar média dos encerrados |
| Presença de julgamento/trânsito | Viável como descritivo | Por coorte, com tempo de acompanhamento |
| Total de movimentos | Pouco informativo | Só descritivo, dentro do tipo; não como eficiência |
| Por comarca (período inteiro) | Viável para cerca de 127–144 sedes | Mostrar N e intervalo; tabela oficial de comarcas |
| Por comarca e ano | Só cerca de 43 sedes | Preferir agregação regional |
| Séries 2019–2025 | Viáveis com ressalvas | Excluir cartas; testar sensibilidade às anomalias de 2019–2020 (§7) |

Próximos passos sugeridos: obter a tabela oficial de comarcas do TJPR e definir a regionalização (IBGE ou divisão do TJPR), registrando a fonte; levar ao orientador as anomalias da §7 antes de interpretar a série.
