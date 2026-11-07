# Métodos e tabelas agregadas da Gold

Data: 08/11/2026. Status: **implementado e testado; construção real ainda não executada**. Este documento descreve o que o código faz (decisões já implementadas). Nenhum resultado de uma construção real dos agregados é afirmado aqui; contagens, durações e primeiros resultados serão registrados em documento próprio depois da execução. Perguntas-guia: `19` §5.5; parâmetros: `20` §4; regra de reativados: `23`.

Unidade de contagem: **processos judiciais públicos** (registros da API que passam pelo catálogo), não vítimas, fatos ou ocorrências. Município do órgão julgador não é município do fato (CLAUDE.md §4).

## 1. Regras gerais

- Toda linha de `gold.agg_*` tem `pergunta` (Q01–Q15) e `n` (unidade de contagem da linha). Nenhuma tabela tem `registro_id`, `numero_processo`, `api_id` nem linhas por processo ou evento.
- Séries: `serie` = `estrita` (filtra `serie_estrita = true`) e `ampliada` (todos), uma linha para cada.
- Tipos de procedimento nunca são somados em tempos, desfechos e taxas (`tipo_procedimento` presente).
- Território: `mesorregiao_id` (10 mesorregiões do Paraná).
- 2026 é parcial: `ano_parcial = true`. O recorte janeiro–agosto existe **somente** em `agg_volume_jan_ago`, para comparar volumes anuais com 2026. Todas as demais tabelas usam todos os meses de todos os anos; a data de corte entra como censura e o estrato `total` junta 2019–2026.
- Estimativas de KM e AJ só com **n >= 30** no estrato; abaixo disso a linha é gravada com estimativas NULL e `estimavel = false`.

## 2. Tabelas

As contagens (SQL `40_agg_contagens.sql`) rodam dentro de `construir_gold`; taxas, tempos e desfechos rodam em `construir_agregados`.

| Tabela | Pergunta | Unidade e numerador | Denominador | Exclusões e limitações |
|---|---|---|---|---|
| `agg_volume` | Q01 | Processos por ano, mês, tipo, mesorregião, série | Não há | 2026 parcial; sede judicial, não local do fato |
| `agg_volume_jan_ago` | Q01 | Idem, só meses 1–8 de cada ano | Não há | Usar apenas para comparar volume anual com 2026 |
| `agg_taxa` | Q02 | Processos por ano × tipo × série × mesorregião; `taxa_bruta_100k`, `taxa_eb_100k` | `pop_feminina` (Censo 2022); população zero ou ausente gera NULL | Razão entre processos na sede e população: **não é taxa de violência**; população fixa de 2022 em todos os anos |
| `agg_categoria` | Q03 | Processos por categoria analítica | Não há | Categorias se sobrepõem: não somar |
| `agg_mpu` | Q04 | Processos de MPU; `n_com_decisao`, `n_deferimento`, `n_parcial`, `n_indeferimento`, `n_revogadas` | `n` | Movimento genérico não comprova decisão; ausência de evento não prova que não houve |
| `agg_mpu_medida` | Q06 | Processos por tipo de medida (complemento tabelado) | Não há | Um processo pode ter várias medidas |
| `agg_tempo` | Q05, Q07, Q08, Q09 | Duração até o marco (§3.2) | `n` do estrato | Marcos dependem do registro dos movimentos |
| `agg_desfecho` | Q10 | Incidência acumulada por causa (§3.3) | `n` do estrato | Só ação penal e inquérito |
| `agg_cautelar` | Q13 | Processos por categoria; `n_flagrante`, `n_preventiva`, `n_liberdade_provisoria_concedida` | `n` | Subcontagens são marcos, não desfechos finais |
| `agg_qualidade_orgao` | Q14 | Por órgão julgador: `n`, `media_movimentos`, `mediana_movimentos`, `n_processos_com_duplicado` | Não há | Diferenças entre órgãos refletem composição e registro, não eficiência |
| `agg_cobertura_cnj` | Q14 | `n_base`, `n_cnj`, `pct` por ano e medida | Casos novos do CNJ (`config/gold/ref_cnj_casos_novos.csv`) | Universo e definição podem diferir; 2026 parcial |
| `agg_pipeline` | Q15 | Execuções de coleta e versão de regras | Não há | Metadados de procedência |

Mapeamento das perguntas restantes: **Q12** (órgão especializado × comum) é respondida pelo estrato `orgao_especializado` de `agg_tempo` (`agg_desfecho` não o tem), pela divisão `orgao_especializado` de `agg_mpu` e pelo contexto de `agg_qualidade_orgao`. **Q11** (fluxo, mineração de processos) não tem tabela agregada e fica para a fase de análise.

## 3. Métodos

### 3.1 Taxas: Bayes empírico global (`agg_taxa`)

Para cada ano × tipo × série, sobre as 10 mesorregiões, com casos `n_i` e população feminina `P_i` (só `P_i > 0`):

- razão bruta `r_i = n_i / P_i` e média global `m = Σn / ΣP`;
- variância de Marshall `s² = max( Σ P_i (r_i − m)² / ΣP − m / P̄ , 0 )`, com piso em zero;
- fator `c_i = s² / (s² + m / P_i)` (0 se o denominador for 0);
- estimativa `eb_i = m + c_i (r_i − m)`, multiplicada por 100.000.

Mesorregiões com população zero ou ausente recebem NULL. A estimativa encolhe taxas instáveis em direção à média global; é descritiva e não corrige subcontagem.

### 3.2 Tempos: Kaplan-Meier com censura (`agg_tempo`)

Duração do ajuizamento ao marco, censurada em `data_corte` quando o marco não foi observado.

| Pergunta | Marco | Tipo |
|---|---|---|
| Q05 | `decisao_mpu` | MPU |
| Q07 | `revogacao_mpu` (só deferidas ou parciais) | MPU |
| Q08 | `recebimento_denuncia` | Ação penal e inquérito |
| Q09 | `sentenca` | Ação penal |

Estratos: `total`, `ano`, `mesorregiao` e órgão especializado. Regras: n < 30 não é estimável; mediana não alcançada gera NULL (`mediana_alcancada = false`); `pct_evento_ate_2/30/365/730` é o percentual com o marco até 2, 30, 365 e 730 dias (`1 − S(t)`); o percentual é NULL quando o horizonte excede a maior duração observada do estrato **ou** quando há menos de 30 observações em risco (duração ≥ horizonte). IC 95% em `ic95_inf` e `ic95_sup`. Em MPU, `reativado` não se aplica.

### 3.3 Desfechos: Aalen-Johansen exato em tempo discreto (`agg_desfecho`, Q10)

Riscos competitivos com as causas 1 `CONDENACAO`, 2 `ABSOLVICAO`, 3 `EXTINCAO_PUNIBILIDADE`, 4 `PRESCRICAO` e 5 `OUTRO_ENCERRAMENTO` (agrupa `SEM_MERITO`, `REJEICAO_DENUNCIA`, `ARQUIVAMENTO_INVESTIGACAO` e `ENCERRADO_SEM_DESFECHO`); `EM_ANDAMENTO` é a censura, para ação penal e inquérito (MPU excluída). O estimador é **exato**, sem jitter nas durações empatadas; vale `Σ CIF = 1 − S` exatamente. Horizontes de 365, 730, 1095 e 1825 dias (`ia_365` a `ia_1825`); NULL além do acompanhamento e quando há menos de 30 observações em risco no horizonte (mesma regra do KM; vale no banco e na exportação). Variantes: `principal` (exclui processos com `reativado = true`) e `com_reativados`. Estratos: `total`, coorte (2019–2021, 2022–2023, 2024–2026) e mesorregião dentro da coorte 2019–2021. n < 30 gera `estimavel = false`.

Interpretação: probabilidade acumulada de cada trajetória registrada nos metadados, não eficácia nem causalidade.

## 4. Supressão e exportação

A supressão ocorre **somente na exportação**; o banco guarda os dados completos.

- Limite **5** em toda tabela suprimida, exceto `agg_qualidade_orgao` (limite **10**, agrupada por mesorregião). `agg_cobertura_cnj` e `agg_pipeline` não sofrem supressão.
- **Supressão secundária** dentro dos grupos: se só uma célula do grupo é suprimida, suprime-se também a menor das restantes.
- **Subcontagens** abaixo do limite são suprimidas individualmente, com `suprimido_parcial = true` (`agg_mpu`, `agg_cautelar`).
- **Estimativas seguem a contagem do evento:** quando `n_eventos` (`agg_tempo`) ou `n_desfecho` (`agg_desfecho`) é anulado (supressão primária ou subcontagem < 5), as estimativas dependentes (mediana, IC, `pct_evento_ate_*`; `ia_*`) também saem vazias, e a linha recebe `suprimido_parcial = true`.
- **Subcontagens aditivas de `agg_mpu`:** `n_deferimento`, `n_parcial` e `n_indeferimento` somam `n_com_decisao`. Se exatamente uma das três é anulada, anula-se também a menor das outras duas (`suprimido_parcial = true`), para que a anulada não seja recuperada por subtração.
- **Arredondamento:** em `agg_tempo` (`n`, `n_eventos`) e `agg_desfecho` (`n`, `n_desfecho`), as contagens publicadas são arredondadas ao múltiplo de 10 mais próximo (meio para cima; 5 a 9 viram 10; suprimidas ficam vazias). Isso impede recuperar células suprimidas de `agg_taxa` por subtração dos totais desses estratos. O manifesto registra `arredondamento` (`tabelas`, `base`). As demais tabelas não são arredondadas.
- Células suprimidas ficam com `n` e estimativas vazios, e `suprimido = true`. A coluna `estimavel` é mantida.
- Para evitar recuperação entre tabelas, a exportação **colapsa `agg_volume` e `agg_mpu` sobre a mesorregião**. Os volumes por mesorregião continuam em `agg_taxa` e `agg_volume_jan_ago`.
- `agg_cobertura_cnj` e `agg_pipeline` saem sem supressão.
- **Consistência:** a exportação lê todas as tabelas em um único snapshot (`REPEATABLE READ`, somente leitura, quando a conexão não tem transação aberta). Se a pasta de destino já existe, não é sobrescrita: cria-se `<data_corte>_<versao>_<timestamp UTC>` e o caminho efetivo é devolvido.
- **Risco residual documentado:** `agg_categoria` e `agg_mpu_medida` saem no nível de mesorregião. As categorias se sobrepõem, então não particionam os totais; `agg_mpu_medida` conta linhas de complemento, não processos. A supressão por célula protege cada linha, mas a recuperação por diferença entre tabelas não foi eliminada para essas duas.
- Saída: `outputs/publicacao/<data_corte>_<versao>/`, um CSV por tabela e `manifesto.json` (SHA-256 de cada arquivo, regras aplicadas, versão e data de corte). `outputs/` não é versionado.

## 5. Orquestração e comandos

`construcao_gold` executa a Gold e, em seguida, os agregados (duas transações); é pulada quando a Silver carrega 0 registros. A exportação é **manual**. Comandos: `gold-construir`, `gold-agregados`, `gold-exportar` (`readme.md`). O DDL dos agregados tem migração protegida: só age se existirem os nomes antigos de coluna.

## 6. Limitações conhecidas e o que fica para depois

- **Recuperabilidade dentro da linha:** a supressão individual de uma única subcontagem de MPU pode, em tese, ser recuperada por diferença com `n` e as demais subcontagens da mesma linha. Ponto a tratar antes da publicação.
- Moran/LISA (autocorrelação espacial) e mineração de processos ficam para a fase de análise.
- O destino da publicação (dashboard) fica para o plano do dashboard.
- Os parâmetros (n >= 30, limites 5 e 10) são regras de trabalho, não garantia de anonimização (CLAUDE.md §13).
