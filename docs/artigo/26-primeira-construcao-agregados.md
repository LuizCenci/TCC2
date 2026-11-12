# Primeira construção dos agregados e exportação

Data: 07/11/2026. Status: **verificado**. Execução real de `gold-construir` → `gold-agregados` → `gold-exportar`, versão de regras `gold-2026-11-07`, com o PC mantido acordado. Os números abaixo são **primeiros resultados descritivos do acervo público** e não medem incidência de violência (CLAUDE.md §4). Métodos e regras: `25`.

## 1. Execução

| Etapa | Duração | Saída |
|---|---|---|
| `gold-construir` (inclui as contagens `sql/40`) | 67 s | 147.020 processos; metas do `24` mantidas |
| `gold-agregados` (taxa, tempo, desfecho) | 14 s | `agg_taxa` 1.260 linhas, `agg_tempo` 210, `agg_desfecho` 560 |
| `gold-exportar` | menos de 1 s | `outputs/publicacao/2026-11-05_gold-2026-11-11/` (12 CSV + `manifesto.json`, cerca de 1 MB; não versionado) |

Linhas das tabelas de contagem:

| Tabela | Linhas |
|---|---:|
| `agg_volume` | 10.027 |
| `agg_volume_jan_ago` | 1.047 |
| `agg_categoria` | 6.859 |
| `agg_mpu` | 224 |
| `agg_mpu_medida` | 1.293 |
| `agg_cautelar` | 1.036 |
| `agg_qualidade_orgao` | 313 |
| `agg_cobertura_cnj` | 24 |
| `agg_pipeline` | 3 |

## 2. Primeiros resultados (banco, sem supressão)

**Q05: tempo até a decisão da MPU** (KM; pedidos sem decisão censurados na data de corte; 19.364 MPUs, 15.165 com decisão por código):
- mediana: 1 dia;
- decididas em até 2 dias: 66,9%; em até 30 dias: 77,4%.

A mediana sem censura, de 0 dia, aparece no `18`. Com censura, a proporção cai porque os pedidos sem decisão registrada contam como ainda não decididos. Isso não significa que eles não foram decididos: a decisão pode ter sido registrada por outro movimento (`12` §5).

**Q09: tempo até a sentença na ação penal** (KM):

| Série | Processos | Mediana | IC 95% | Sentenciados em 1 ano | Em 2 anos |
|---|---:|---|---|---:|---:|
| Estrita | 58.384 | 758 dias | 751–765 | 25,5% | 48,4% |
| Ampliada | 60.611 | 752 dias | — | — | — |

**Q08: tempo até o recebimento da denúncia:**
- ação penal: mediana de 70 dias (estrita);
- inquérito: mediana não alcançada, porque a maior parte dos inquéritos não chega a denúncia recebida no mesmo registro.

**Q10: desfechos da ação penal, coorte 2019–2021** (Aalen-Johansen exato; série estrita; sem reativados; 24.109 processos). Incidência acumulada:

| Desfecho | 1 ano | 3 anos | 5 anos |
|---|---:|---:|---:|
| Condenação | 10,6% | 35,9% | 46,0% |
| Absolvição | 2,2% | 12,5% | 18,1% |
| Extinção da punibilidade | 4,1% | 8,9% | 11,1% |
| Prescrição | 0,1% | 1,3% | 8,0% |
| Outro encerramento | 3,1% | 5,9% | 8,3% |

Em 5 anos, 91,5% dos processos da coorte tiveram desfecho; os demais seguem em andamento.

**Q02: ações penais públicas por 100 mil mulheres, 2025** (série estrita). A suavização Bayes empírica altera pouco, porque as mesorregiões têm populações grandes.

| Mesorregião | Processos | Taxa bruta | Taxa EB |
|---|---:|---:|---:|
| Centro Ocidental | 417 | 238,7 | 235,7 |
| Centro-Sul | 648 | 233,9 | 232,1 |
| Sudoeste | 592 | 204,2 | 202,9 |
| Norte Pioneiro | 491 | 176,9 | 176,0 |
| Oeste | 1.082 | 150,7 | 150,5 |
| Centro Oriental | 535 | 138,8 | 138,6 |
| Norte Central | 1.258 | 107,2 | 107,2 |
| Sudeste | 205 | 101,1 | 101,5 |
| Noroeste | 300 | 80,9 | 81,3 |
| Metropolitana de Curitiba | 1.355 | 67,8 | 68,0 |

A diferença de cerca de 3,5 vezes entre extremos é do **acervo público**. Ela pode refletir sigilo, prática de registro e estrutura judiciária, e não necessariamente judicialização (`22`, `24` §4). Fica para a análise com a cobertura e a intensidade de registro por órgão (Q14).

**Cobertura das MPUs públicas em relação ao CNJ** (`agg_cobertura_cnj`): 9,0% (2019), 6,0%, 4,7%, 4,3%, 3,5%, 2,8%, 2,7% (2025), 2,4% (2026, parcial). A série é a mesma do `22`.

## 3. Pendências registradas

- Teste `test_ia_sem_censura_igual_proporcao` ficou mais fraco depois da regra de risco mínimo. Corrigir na próxima manutenção.
- As duas transações do orquestrador (Gold e agregados) podem deixar taxa, tempo e desfecho de uma construção anterior se a segunda falhar.
- Os resultados acima são descritivos. Interpretação e sensibilidade (estrita × ampliada, com ou sem 2019–2020) ficam para a fase de análise e para o artigo.
