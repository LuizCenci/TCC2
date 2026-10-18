# Quadro comparativo — SINAN Violência × Datajud

Material de apoio para o artigo e o dashboard. Esta é uma **recomendação de trabalho**: o uso do SINAN como fonte contextual ainda depende de aprovação do orientador. Números e procedência estão em `04-sinan-exploracao-pr-2023-2024.md`.

## 1. Duas portas de entrada, não um funil

As bases não permitem acompanhar o mesmo caso da saúde até a Justiça. Não há identificador comum, e o SINAN é desidentificado. Entre elas existe a etapa policial (boletim de ocorrência e inquérito), que nenhuma das duas registra. Muitas mulheres chegam ao Judiciário sem passar pela saúde, e muitas notificações nunca geram processo.

```text
violência ─┬─> atendimento em saúde ──> SINAN (notificação)
           │            │
           │            └─ encaminhamento ──┐
           └────────────────────────────────┴─> delegacia / BO  ──> MP / Judiciário ──> Datajud (processo)
                                                 (fora das duas bases)
```

Portanto, **não é possível calcular quantas notificações "viraram processo"**. Qualquer razão entre as contagens das duas bases é uma razão entre registros de sistemas diferentes, e não uma taxa de judicialização.

## 2. Quadro comparativo

| Dimensão | SINAN Violência (saúde) | Datajud (Judiciário) |
|---|---|---|
| O que registra | Notificação de caso suspeito ou confirmado atendido em serviço de saúde | Metadados de processo judicial |
| Quem gera o registro | Profissional de saúde (notificação compulsória) | Tribunal, a partir do ajuizamento |
| Porta de entrada | Procurar atendimento de saúde, ou suspeita identificada durante o atendimento | Denúncia, inquérito, pedido de medida protetiva |
| Unidade de contagem | Notificação, que não equivale a vítima; a mesma mulher pode ter várias | Processo, que não equivale a vítima nem a agressão |
| Data principal | Ocorrência (`DT_OCOR`) e notificação | Ajuizamento (`dataAjuizamento`) |
| Território | Município do fato e de residência | Município do órgão julgador (sede) |
| Perfil da vítima | Idade, raça/cor, escolaridade, gestação | Não disponível |
| Vínculo com o autor | Sim (cônjuge, ex, familiar etc.) | Não disponível |
| Local da ocorrência | Sim (residência, via pública etc.) | Não disponível |
| Tipo de violência | Física, psicológica, sexual, patrimonial etc. (não exclusivos) | Indireto, via classes e assuntos da TPU |
| Medida protetiva | Não registra (`MPU` = encaminhamento ao Ministério Público) | Pode constar em classe, assunto ou movimento (a validar) |
| Desfecho | Não registra | Movimentos processuais, com limitações |
| Quem fica de fora | Quem não procurou a saúde ou não foi notificada | Quem não denunciou; processos sigilosos ou mal classificados |
| Filtros de seleção | Acesso à rede e prática local de notificação | Acesso à Justiça, publicidade, classificação |
| Disponibilidade | Microdados anuais (FTP DATASUS); finais até 2024 | API pública, índice atualizado continuamente |

## 3. Encaminhamentos registrados no SINAN

Os encaminhamentos são o indício mais próximo do caminho da saúde para a via policial e judicial. Recorte: notificações de mulheres de 18 anos ou mais, exceto lesão autoprovocada, notificadas no PR em 2023–2024. Os percentuais são de respostas "Sim". As categorias não são exclusivas.

| Encaminhamento | % das notificações |
|---|---:|
| Delegacia de Atendimento à Mulher | 15,6 |
| Outras delegacias | 21,6 |
| Rede de atendimento à mulher | 17,8 |
| Ministério Público | 2,8 |
| Defensoria Pública | 1,4 |

**Leitura correta:** só uma parte das mulheres atendidas na saúde é encaminhada formalmente à via policial ou judicial. Esses números medem **encaminhamento registrado**, não comparecimento nem abertura de processo. Uma ausência de encaminhamento não prova que a mulher não procurou a polícia por conta própria.

## 4. Como usar no TCC

- **Artigo:** subseção curta de contexto. Use o quadro para justificar o que o Datajud não mede (perfil, vínculo, local do fato) e a tabela de encaminhamentos para ilustrar que a judicialização é um recorte parcial da violência que chega aos serviços.
- **Dashboard (opcional):** página de contexto com o quadro e as proporções estaduais, sem desagregação municipal (há muitas células pequenas).
- **Trabalho futuro:** comparar tendências das duas séries e, por comarca, a razão entre registros, dependendo da tabela comarca→municípios do TJPR.
