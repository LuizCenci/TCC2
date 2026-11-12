# Validação externa: base do TCC × painéis do CNJ

Data: 07/11/2026. Status: **verificado** (valores do CNJ extraídos pelo autor em 07/11/2026; contagens da base consultadas na Silver na mesma data). Atende ao `19` §7 e ao `20` §6, item 6. Evidências em `evidencias/validacao_cnj/`:
- `Tabela-Processos-Resultados-Painel-2019-por-Estado-09032020.pdf`, baixado pelo autor;
- `base_por_ano.json`.

## 1. Fontes do CNJ

| Ano | Fonte | Como foi obtida |
|---|---|---|
| 2019 | CNJ, *Monitoramento da Política Judiciária Nacional de Enfrentamento à Violência contra as Mulheres*: tabela por estado, 2018–2019 (PDF de 09/03/2020) | PDF baixado pelo autor. A extração de texto perde os cabeçalhos das colunas; as três colunas usadas foram identificadas pela taxa por 100 mil mulheres ao lado de cada uma (ver nota) |
| 2020–2026 | Painel de Violência contra a Mulher do CNJ ([link](https://justica-em-numeros.cnj.jus.br/painel-violencia-contra-mulher/)), filtro TJPR | Valores anotados manualmente pelo autor em 07/11/2026. **2026 é parcial** e reflete a data da consulta |

**Nota sobre 2019 (PR, colunas de 2019).** São 42.375 casos novos de violência doméstica, ao lado de 730 por 100 mil mulheres; 137 casos novos de feminicídio, ao lado de 2,4 por 100 mil; e 35.341 medidas protetivas, ao lado de 607 por 100 mil. A identificação foi conferida dividindo cada valor pela população feminina do Censo 2022 (5.867.030, `21` §1). Os resultados (722, 2,3 e 602 por 100 mil) ficam próximos das taxas impressas; a pequena diferença é compatível com o denominador populacional de 2019 usado pelo CNJ. As demais colunas, provavelmente sentenças, baixados e pendentes, **não foram identificadas** e não são usadas.

## 2. Comparação

"Base" é o acervo público coletado (`13` §6), por ano de ajuizamento.

| Ano | VD novos (CNJ) | Base sem cartas | % | MPU (CNJ) | Base MPU (1268) | % | Feminicídio novos (CNJ) | Base: feminicídio em ação penal | % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 | 42.375 | 21.428 | 50,6 | 35.341 | 3.171 | 9,0 | 137 | 158 | 115 |
| 2020 | 60.097 | 15.161 | 25,2 | 40.843 | 2.438 | 6,0 | 338 | 120 | 35,5 |
| 2021 | 63.355 | 13.627 | 21,5 | 48.471 | 2.283 | 4,7 | 216 | 94 | 43,5 |
| 2022 | 66.355 | 13.160 | 19,8 | 55.055 | 2.344 | 4,3 | 206 | 100 | 48,5 |
| 2023 | 82.714 | 14.533 | 17,6 | 70.079 | 2.437 | 3,5 | 265 | 115 | 43,4 |
| 2024 | 91.658 | 15.921 | 17,4 | 86.489 | 2.444 | 2,8 | 279 | 114 | 40,9 |
| 2025 | 97.143 | 17.703 | 18,2 | 91.955 | 2.458 | 2,7 | 289 | 114 | 39,4 |
| 2026* | 82.111 | 13.227 | 16,1 | 73.138 | 1.788 | 2,4 | 250 | 61 | 24,4 |

\* A parte do CNJ vai até a data da consulta; a base vai até ajuizamentos de 30/09/2026, com indexação atrasada (`13`). O percentual de 2026 não é comparável aos demais.

Outras contagens de feminicídio na base (assunto 12091), por ano: em qualquer tipo de procedimento, 372, 767, 420, 370, 414, 455, 491 e 359; dessas, em Júri (282), 150, 119, 87, 95, 113, 111, 104 e 53. A contagem em qualquer procedimento **supera** a do CNJ porque soma inquéritos, cautelares, liberdades provisórias e cartas com o mesmo assunto. Por isso, a comparação usa só as ações penais.

## 3. O que a comparação mostra

1. **A base cobre uma fração do total, e essa fração depende do tipo de procedimento.** Os percentuais são razões entre registros públicos e casos novos totais, não taxas de judicialização (CLAUDE.md §6).
   - **Medidas protetivas:** de 2,7% a 6,0% em 2020–2025, coerente com os 4,9% públicos que o CNJ (2022) mediu para jan/2020–mai/2022 (`12`).
   - **Violência doméstica em geral:** cerca de 17–25%.
   - **Feminicídio** (ações penais): cerca de 35–49%.

   As conclusões sobre medidas protetivas valem, portanto, para uma fatia pequena do total. As de ações penais, sobretudo as de feminicídio, se apoiam numa fatia bem maior.
2. **A cobertura das MPUs cai ao longo do tempo** (6,0% em 2020 → 2,7% em 2025). O total de MPUs no CNJ mais que dobra (40.843 → 91.955), enquanto a base fica estável (cerca de 2.300–2.500 por ano). Hipótese, não verificada: o sigilo cresce junto com o volume. Consequência: **a série de MPUs públicas não acompanha a tendência real de MPUs**, e o dashboard deve dizer isso.
3. **A cobertura geral também cai** (25% → 18%). O crescimento real de casos novos (60 mil → 97 mil) aparece só em parte na base (15 mil → 18 mil). Tendências da base precisam ser lidas como tendências do **acervo público**.
4. **2019 é anômalo:** a base ultrapassa os casos novos de feminicídio do CNJ (115%) e tem 50,6% dos casos de violência doméstica, contra cerca de 20% nos demais anos. Isso reforça as anomalias de registro de 2019–2020 já documentadas (`08` §7). A tabela de 2019 também é de outro produto do CNJ (antes do painel), com critério possivelmente diferente. Recomendação: tratar 2019 como **ano de sensibilidade** nas séries.
5. **Divergências esperadas e explicadas** (`19` §7):
   - universo público × total;
   - classes: a base exclui cartas, mas inclui inquéritos e cautelares, e o critério do painel não foi conferido;
   - catálogo de assuntos × critério do CNJ;
   - data de corte (2026);
   - unidade: registro na base × caso novo no CNJ.

## 4. Implicações para a Gold e o dashboard

- **Página "Cobertura e qualidade" (Q14):** incluir esta tabela, com o percentual da base em relação ao CNJ por ano e tipo de procedimento.
- **Rótulos das séries:** "processos públicos". Nas séries de MPU, avisar que a cobertura caiu de cerca de 6% para cerca de 3% no período.
- **Taxas por 100 mil mulheres (Q02):** mantêm o rótulo "processos públicos" e o aviso de cobertura. A diferença de cobertura entre tipos de procedimento recomenda **calcular as taxas por tipo**, nunca com todos os tipos somados.
- **Sensibilidade:** séries com e sem 2019 (e 2020).

## 6. Atualização de 11/11/2026: critérios do painel do CNJ

As seções 1 a 5 acima ficam como histórico e foram **substituídas** neste ponto pela comparação com os critérios do painel (https://justica-em-numeros.cnj.jus.br/painel-violencia-contra-mulher/, lidos em 11/11/2026).

- **Violência doméstica:** assuntos 10948, 10949, 11979, 12194, 12196, 14226, 14227, 14228, 14229, 14942, 14943, 14944, 14945, 14097 e 14098, ou classes 1268, 12423 e 15309, excluídos os processos de feminicídio. Na base, as cartas precatórias também são excluídas.
- **Feminicídio:** assuntos 12091 e 12358, desde que a classe atual seja ação penal (282, 283, 1033, 1317, 10943, 10944, 11037, 11528), execução penal (386, 1714, 11399, 12727, 12728, 12729, 14696), inquérito (279) ou ato infracional (1464). Conta consumado e tentado. A base é só de 1º grau.
- **Medidas protetivas:** o total do painel é de **decisões** (concedidas, denegadas, revogadas, prorrogadas e homologadas), não de processos. Não é comparável com a base e saiu da comparação.
- **2019** deixa de ser comparado: a referência vem de outra publicação do CNJ, com critério não informado. Os denominadores de 2020 a 2025 (TJPR, 1º grau, casos novos) foram conferidos pelo autor e coincidem com `config/gold/ref_cnj_casos_novos.csv`.
- Filtros aplicados à versão mais recente de cada registro, com os assuntos dele e a classe atual (`gold.fato_processo`); SQL em `src/datajud_tcc/gold/sql/40_agg_contagens.sql`.

| Ano | Violência doméstica: base | CNJ | % | Feminicídio: base | CNJ | % |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | 13.110 | 60.097 | 21,8 | 127 | 338 | 37,6 |
| 2021 | 12.924 | 63.355 | 20,4 | 108 | 216 | 50,0 |
| 2022 | 12.749 | 66.355 | 19,2 | 109 | 206 | 52,9 |
| 2023 | 14.034 | 82.714 | 17,0 | 121 | 265 | 45,7 |
| 2024 | 15.315 | 91.658 | 16,7 | 123 | 279 | 44,1 |
| 2025 | 17.025 | 97.143 | 17,5 | 127 | 289 | 43,9 |
| 2026 (parcial) | 12.724 | 82.111 | 15,5 | 78 | 250 | 31,2 |

Leitura: razão entre contagens de registros com critérios equivalentes, não cobertura exata nem taxa de judicialização. Exportação: `outputs/publicacao/2026-11-05_gold-2026-11-11/`; versão de regras `gold-2026-11-11`.

## 5. Pendentes e julgados

Não são necessários para esta validação. A comparação usa **casos novos**, que correspondem ao que a base mede (processos por ano de ajuizamento). Pendentes, baixados e julgados medem estoque e produtividade, que a base pública não reproduz.
