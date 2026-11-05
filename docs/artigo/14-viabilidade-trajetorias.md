# Viabilidade de trajetórias processuais, desfecho e clusterização

Data: 05/11/2026. Origem: orientação recebida pelo autor, que propõe transformar as movimentações em **trajetórias multidimensionais**, obter um **resultado** do processo (condenação ou não, gravidade) e aplicar **classificação** (método do orientador) ou **clusterização** para comparar andamentos entre órgãos e cidades.

Status: §1–§3 **verificados** na Bronze (procedimentos principais, 2019–2025; 2026 entra após a recoleta, `13`); §4–§6 **proposta de trabalho**.

Evidências: `evidencias/trajetorias_viabilidade_20261105/viabilidade_trajetorias.json`. Script: `evidencias/scripts/viabilidade_trajetorias.py` (lê o extrato sem identificadores de `work/analise/`).

## 1. Existe um campo de resultado?

**Não.** A API não tem campo de desfecho nem de "grau de violência" (inventário completo em `docs/exemplos/campos_api.json`). Mas o **desfecho pode ser derivado dos códigos de movimento**, pela hierarquia oficial da TPU (`08` §2):

| Desfecho derivado | Códigos TPU | Caminho na TPU |
|---|---|---|
| Condenação / condenação parcial | 219 Procedência / 221 Procedência em parte | Magistrado > Julgamento > Com resolução do mérito |
| Absolvição | 220 Improcedência; 11876/11877 Absolvição sumária | idem |
| Extinção da punibilidade | 11878 Prescrição, 11879 Decadência/perempção, 1046 Renúncia/perdão, 1047 Retratação, 1042 Morte do agente, 11411 Cumprimento da suspensão condicional, 12735 Cumprimento de ANPP… | idem > Extinção da punibilidade |
| Extinção sem mérito | 455, 459–461, 463, 471 | Magistrado > Julgamento > Sem resolução de mérito |
| Denúncia rejeitada | 402 | Magistrado > Decisão > Rejeição |
| Arquivamento da investigação | 1063, 12430 | Magistrado > Decisão > Determinação |

**A confirmar com o especialista** (`09`, pergunta 14): no processo penal, "Procedência" e "Improcedência" da denúncia correspondem a condenação e absolvição.

## 2. Cobertura do desfecho (procedimentos principais, N = 77.417)

Primeiro desfecho observado por processo:

| Desfecho | N | % |
|---|---:|---:|
| Condenação | 20.276 | 26,2 |
| Condenação parcial | 5.113 | 6,6 |
| Absolvição (inclui sumária) | 10.021 | 12,9 |
| Extinção da punibilidade (prescrição 5,0%; decadência/perempção 4,9%; morte 2,0%; renúncia 1,3%; outras) | 11.849 | 15,3 |
| Arquivamento da investigação / determinado | 8.467 | 10,9 |
| Denúncia rejeitada | 2.001 | 2,6 |
| Sem mérito | 2.293 | 3,0 |
| **Sem desfecho observado** | **17.397** | **22,5** |

Processos sem desfecho observado, por ano de ajuizamento: 5,9% (2019), 6,3%, 9,4%, 11,7%, 22,6%, 36,6%, **68,2% (2025)**. Os processos recentes ainda não terminaram, ou seja, são **censurados**. Mediana de dias até o desfecho: condenação 514; absolvição 637; prescrição 1.270; arquivamento da investigação 202.

Por categoria de assunto (proposta do `07` §8): feminicídio 40% de condenação e 13% de condenação parcial; descumprimento de MPU 35%; lesão 27%; violência psicológica 17%, com 37% ainda sem desfecho.

**Conclusão:** o desfecho é derivável para cerca de **3/4 dos procedimentos principais** e para mais de 90% das coortes 2019–2021. É viável como variável de resultado, desde que a censura seja tratada.

## 3. As trajetórias são reconstruíveis?

Sim. Com cerca de 40 eventos semânticos definidos por código (distribuição, redistribuição, denúncia recebida ou rejeitada, audiências, prisão em flagrante ou preventiva, liberdade provisória, decisões de MPU, julgamento, trânsito, arquivamento, reativação), cada procedimento principal tem **mediana de 10 eventos** (6 distintos). As variantes mais frequentes são legíveis:

```text
1.404  distribuição > denúncia recebida > audiência de instrução e julgamento > condenação > trânsito > arquivamento definitivo
1.104  distribuição > denúncia recebida > audiência de instrução e julgamento > absolvição > trânsito > arquivamento definitivo
1.068  distribuição > redistribuição > liberdade provisória > denúncia recebida > audiência de instrução e julgamento
  814  arquivamento da investigação > trânsito > arquivamento definitivo
```

Há **12.570 variantes distintas** nos 8 primeiros eventos. A diversidade é alta, o que é típico de dados processuais: é preciso agregar estados ou usar distâncias entre sequências, e não comparar variantes exatas.

## 4. "Grau de violência": não existe; há proxies jurídicos, a rotular como tal

Não há variável de gravidade do fato (CLAUDE.md §7: não inventar). É possível construir uma **gravidade do enquadramento e da resposta processual**, explicitamente rotulada como proxy:

- **enquadramento:** categoria do assunto (feminicídio > lesão > descumprimento > psicológica/ameaça); 5555 Crime tentado; classe 282 (Júri);
- **resposta cautelar:** prisão em flagrante (175), conversão em preventiva (12140), manutenção da preventiva (15032), MPU concedida e **tipo de medida** (complementos: afastamento do lar, monitoramento eletrônico, suspensão de porte de arma).

Esses indicadores medem **como o caso foi classificado e tratado**, não a violência sofrida.

## 5. Proposta: trajetórias multicanal

Unidade: procedimento principal, com tempo em semanas ou meses desde o ajuizamento, até o desfecho ou até a data da coleta.

| Canal | Estados (exemplo) | Fonte |
|---|---|---|
| Fase processual | investigação → denúncia recebida → instrução → julgado → trânsito → arquivado | movimentos 391, 12749/12750, 219–221…, 848, 246 |
| Situação cautelar | solto / preso em flagrante / preventiva / liberdade provisória | 175, 12140, 15032, 818 |
| Desfecho | em andamento / condenação / absolvição / extinção / arquivamento | §1 |
| Território (atributo) | órgão atual, município-sede, região; redistribuições | capa + movimento 36 |

**Medidas protetivas** formam outro tipo de procedimento (classe 1268). Podem ter trajetória própria (concessão → prorrogação → revogação → arquivamento), mas **não são ligáveis** ao processo principal do mesmo fato (`07` §3).

**Métodos possíveis:**

- *Análise de sequências* (estado por mês; distâncias de optimal matching ou Hamming; clusterização hierárquica ou PAM). Ferramenta de referência: TraMineR/seqHMM (R). Em Python há opções menos maduras.
- *Process mining* (log de eventos: caso = processo, atividade = evento, tempo = `dataHora`; pm4py): descoberta de fluxos, variantes e comparação entre órgãos.
- *Método do orientador*: **perguntar** qual é e que formato de entrada espera (sequências de estados? séries temporais multivariadas?). O modelo da Silver (`10`, tabela `deriv.evento`) já produz a entrada genérica (processo, evento, data).

## 6. Cuidados que condicionam a interpretação

1. **Censura:** trajetórias de 2024–2026 estão incompletas. Comparar coortes com o mesmo tempo de acompanhamento (por exemplo, os primeiros 18 meses) ou usar métodos que tratem censura.
2. **Cobertura:** só o acervo público (`12`; cerca de 5% das MPUs do TJPR). Clusters descrevem processos públicos, que podem diferir sistematicamente dos sigilosos.
3. **Prática de registro × andamento real:** varas registram movimentos de forma diferente. A "tramitação direta MP–polícia" cresce a partir de 2022, e há as anomalias de 2019–2020 (`08` §7). Clusters por órgão podem refletir **forma de registro**, não diferença de andamento. Testar a sensibilidade agregando eventos de rotina.
4. **Composição:** diferenças entre órgãos ou cidades exigem controlar por categoria, classe e coorte antes de se falar em diferença de andamento (CLAUDE.md §4.10).
5. **Órgão atual:** usar também o órgão de cada movimento para trajetórias com redistribuição (CLAUDE.md §4.6).

**Avaliação:** **implementável**, com o desfecho derivado por código, trajetórias multicanal a partir do `deriv.evento` e clusterização como análise exploratória. O próximo passo técnico é a Silver (`10`), seguida de um protótipo com uma coorte completa (por exemplo, 2019–2021).
