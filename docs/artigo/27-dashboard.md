# Dashboard de resultados

Data: 08/11/2026. Status: **implementado e testado; conferido visualmente em navegador; publicação no Streamlit Community Cloud ainda não feita** (será feita pelo autor). O dashboard apenas exibe os agregados do `26`; não recalcula estatísticas nem cria agregados novos. Código em `dashboard/`, instruções em `dashboard/README.md`. Limites de interpretação: CLAUDE.md §4.

## 1. Objetivo e público

Mostrar os resultados do TCC de forma visual e interativa: gráficos e mapa da judicialização da violência contra a mulher no Paraná. Público: banca, orientador e autor; usos previstos são capturas para o artigo e os slides, navegação na defesa (dezembro de 2026) e um link público. Pedido do autor: quem abrir o link deve entender logo que **todos os resultados vêm exclusivamente dos metadados públicos do Datajud (CNJ)**. A página inicial abre com essa frase e com os quadros "Mostra" e "Não mostra".

O app não consulta banco nem API, não atualiza sozinho e não tem contas de usuário.

## 2. Exportação usada

| Item | Valor |
|---|---|
| Pasta | `outputs/publicacao/2026-11-05_gold-2026-11-11/` (12 CSVs e `manifesto.json`, versionada) |
| `versao_regras` | `gold-2026-11-11` |
| `data_corte_max` | 2026-11-05 |
| SHA-256 do `manifesto.json` | `faa4b64e02311c87eae893f34f1aa6a5a7c6870c2d06b48a2888a4a9352dcff1` |

O app confere o SHA-256 de cada CSV contra o manifesto a cada execução do aplicativo (`dashboard/app.py`). Se um arquivo faltar ou diferir, mostra o nome do arquivo e nenhum número. Os CSVs nunca são editados; correções de rótulo existem só na exibição. A pasta é configurada num único lugar (`PASTA_EXPORTACAO` em `dashboard/painel/config.py`).

**Atualização (12/11/2026, tabelas e flagrante):** as tabelas de tempo (ações penais, medidas protetivas e Território) passaram a usar colunas numéricas ("Mediana (dias)", "Processos (n, arredondado)" e, em medidas protetivas, "Até 2/30/365 dias (%)"), exibidas com `NumberColumn(format="localized")`, de modo que a ordenação é pelo valor e não alfabética. "IC 95% (dias)" é texto "inf–sup"; "Situação" informa "suprimido", "não estimável" ou "mediana não alcançada" quando não há mediana (nunca zero). Na resposta cautelar, uma nota explica que o código de flagrante (175) quase deixou de ser usado a partir de 2021 (valores suprimidos) enquanto cresce o flagrante convertido em preventiva (12140), contado em "Prisão preventiva".

**Atualização (11/11/2026):** a exportação `gold-2026-11-07` foi substituída pela `gold-2026-11-11`, cuja única mudança de conteúdo é a tabela de cobertura (`agg_cobertura_cnj`, ver `22` §6). A página "Cobertura e qualidade" compara a base com o painel do CNJ pelas medidas "Violência doméstica (critério do CNJ)" e "Feminicídio (critério do CNJ)", só de 2020 em diante; as medidas protetivas do painel são decisões, não processos, e não são comparadas. O rodapé da visão geral cita a faixa de violência doméstica de 2020 a 2025 (16,7% a 21,8%). A nota de 2019 como anômalo e a razão de medidas protetivas foram retiradas.

## 3. Páginas e perguntas

Navegação por menu lateral; a lateral também tem o filtro global de série (estrita, padrão; ampliada). Mapeamento das perguntas conforme o `25`.

| Página | Tabelas | Perguntas |
|---|---|---|
| Visão geral | `agg_pipeline`, `agg_tempo`, `agg_desfecho`, `agg_cobertura_cnj`, `manifesto.json` | Q15 (procedência), Q14 (cobertura no rodapé) e destaques de Q05, Q09 e Q10 |
| Volume no tempo | `agg_volume`, `agg_cautelar` | Q01, Q03 |
| Território | `agg_taxa`, `agg_tempo` (estrato mesorregião) | Q02 e tempos por mesorregião (Q05, Q08, Q09) |
| Medidas protetivas | `agg_mpu`, `agg_mpu_medida`, `agg_tempo` | Q04, Q05, Q06, Q07 e Q12 (filtro de órgão especializado) |
| Ações penais | `agg_tempo`, `agg_desfecho`, `agg_cautelar` | Q08, Q09, Q10, Q13 |
| Cobertura e qualidade | `agg_cobertura_cnj`, `agg_qualidade_orgao` | Q14 |
| Sobre os dados | `agg_pipeline`, `manifesto.json` | Q15 |

Q11 (fluxo, mineração de processos) não tem tabela agregada e não aparece (`25`).

Detalhes por página:

- **Visão geral:** números lidos dos CSVs (nada digitado no código): processos na base analítica (147.020, linha da Gold em `agg_pipeline`; o artigo cita 147.002 registros coletados, e a diferença são os 18 registros de 2026 que saíram do índice), mediana até a decisão da MPU, mediana até a sentença na ação penal e condenação em 5 anos (coorte 2019–2021). O total não muda com a série. O rodapé traz a faixa de cobertura das MPUs frente ao painel do CNJ, a data de corte e a versão das regras.
- **Volume no tempo:** série mensal por tipo (abre com Ação penal, Inquérito e MPU), com 2026 marcado como parcial; comparação entre anos (padrão: totais anuais de anos completos, com 2026 parcial hachurado; opção "Janeiro a agosto"); categorias de violência por ano.
- **Território:** mapa coroplético das 10 mesorregiões com ano e tipo à escolha (padrão: Ação penal, 2025, série estrita, taxa suavizada Bayes empírico, faixa de cerca de 68 a 236 processos por 100 mil mulheres, o mesmo recorte do `26`), opção de taxa bruta, ranking em barras e tempos medianos por mesorregião (o seletor de marco oferece só os marcos existentes para o tipo escolhido, com padrão Sentença ou Decisão da MPU; tipos sem marco mostram uma mensagem explicativa).
- **Medidas protetivas:** decisões e revogações por ano, tempo até a decisão (mediana e percentuais em até 2, 30 e 365 dias) e tipos de medida.
- **Ações penais:** tempo até denúncia e sentença (mediana e IC 95%), desfechos acumulados por coorte (variantes `principal` e `com_reativados`) e resposta cautelar (flagrante, preventiva, liberdade provisória).
- **Cobertura e qualidade:** base pública e painel do CNJ por ano e medida; qualidade por órgão, só o que a supressão deixa visível.
- **Sobre os dados:** fonte, recorte, pipeline, supressão, séries, limitações, nomes de medida, 2019 como ano de sensibilidade e código-fonte.

## 4. Regras de exibição

Definidas na spec do dashboard (rascunho interno, não versionado) e resumidas aqui.

- **Suprimido:** célula com `suprimido=true` aparece como "suprimido", nunca 0; em séries o ponto fica ausente com nota; `suprimido_parcial=true` gera aviso de subcontagens ocultas. Recorte inteiramente suprimido mostra "Todos os valores deste recorte foram suprimidos para proteger a privacidade." em vez de gráfico vazio.
- **Estimável:** `estimavel=false` mostra "não estimável" e `mediana_alcancada=false` mostra "mediana não alcançada", nunca um número. Tempos e desfechos vêm arredondados na base 10 (dito nas páginas).
- **Rótulos:** unidade sempre "processos públicos" (nunca vítimas ou casos); a taxa é "processos públicos por 100 mil mulheres (Censo 2022)", nunca "taxa de violência". Códigos viram nomes em português; mesorregiões vêm de `config/gold/ref_municipio_pr.csv`.
- **2026 parcial:** todo rótulo de ano 2026 vira "2026 (parcial)"; comparações entre anos usam jan–ago.
- **Contagens:** exibidas como `1.234` (nunca `1.234,0` por leitura como float) e decimais como `12,5`.
- **Gráfico:** rodapé com definição, unidade, série e arquivo de origem; botão de download em CSV dos dados exibidos.
- **Cobertura acima de 100%:** feminicídio em 2019 dá 115%; a coluna se chama "razão base pública / CNJ (%)", é razão entre contagens de registros, e 2019 é ano de sensibilidade (`22` §4).
- **Mesorregião sem dado no mapa:** cinza `#BDBDBD` com "suprimido" ou "sem dado" no hover; as 10 mesorregiões sempre aparecem.

### Decisões tomadas na implementação

- **Comparação entre anos:** por padrão soma os meses 1–12 de cada ano (2026: meses 1–9, rótulo "2026 (parcial, jan–set)", barra hachurada e com opacidade reduzida, com nota de não comparabilidade); o seletor `volume_periodo` oferece "Janeiro a agosto", que soma os meses 1–8 de `agg_volume` (nível estadual). Ano ou tipo com algum mês suprimido fica sem barra e é listado como suprimido. A série mensal abre com Ação penal, Inquérito e MPU.
- **Categorias por ano:** `agg_categoria` não tem linha estadual; mostram-se só as combinações em que nenhuma mesorregião está suprimida. Categorias se sobrepõem e nunca são somadas.
- **Cobertura no rodapé da Visão geral:** usa só os anos completos e fora da sensibilidade, 2020–2025 (2,7% a 6,0%), coerente com o artigo e o `22`; 2019 é ano de sensibilidade.
- **Tipos de medida:** são um limite inferior ("mínimo, soma das mesorregiões não suprimidas"), não um total.
- **Nomes de medida:** truncados ou com codificação quebrada na própria fonte (Datajud); corrigidos só no rótulo exibido. Nomes truncados iguais podem reunir medidas distintas.

## 5. Decisões do autor

| Tema | Decisão |
|---|---|
| Ferramenta | Streamlit |
| Navegação | Páginas no menu lateral, filtros na lateral |
| Página inicial | Frase de abertura, quadros "Mostra" e "Não mostra", números principais e cobertura no rodapé |
| Paleta | Lilás (Agosto Lilás), inclusive na escala do mapa |
| Repositório | O mesmo `LuizCenci/TCC2` |
| Exportação | Manual, fora do orquestrador, ao menos até a defesa |
| Prazo | Pronto para a defesa, em dezembro de 2026 |

## 6. Geometria e fonte

As mesorregiões são geradas uma única vez, offline, por `dashboard/scripts/gerar_mesorregioes.py`: dissolução dos municípios da malha do IBGE (`config/gold/malha_municipios_pr.geojson`, 399 municípios) pela correspondência `config/gold/ref_municipio_pr.csv`, com simplificação de 0,005 grau. O resultado, `dashboard/dados/mesorregioes_pr.geojson`, é versionado; o app em produção só o lê. População: Censo 2022 (`21`). Dependências do Cloud: `streamlit`, `pandas` e `plotly`.

## 7. Limitações

- Processos públicos de primeiro grau do TJPR não são vítimas, ocorrências nem incidência da violência.
- A localização é a do órgão julgador, não a do fato nem a da residência; a taxa por 100 mil mulheres usa população fixa de 2022 em todos os anos e não é taxa de violência.
- Supressão (limite 5, com ressalvas do manifesto) e arredondamento na base 10 limitam o detalhe; somas de agregados suprimidos não são totais.
- 2026 é parcial; 2019 é ano de sensibilidade.
- Exibição descritiva: sem causalidade, sem avaliação de políticas e sem comparação de eficiência entre unidades.
- Os dados são uma fotografia congelada (corte em 05/11/2026); a atualização é manual.
- O plano gratuito do Streamlit Community Cloud hiberna o app.

## 8. Testes e conferências

- `.\.venv\Scripts\python.exe -m pytest tests/dashboard -q`: **58 testes passando**, sem Streamlit em execução (carga e integridade SHA-256, formatação, rótulos, figuras, tratamento de suprimido e não estimável) e com `AppTest` (pasta corrompida, filtro extremo).
- Conferência visual feita em navegador, em 1400×900, nas 7 páginas. Problemas encontrados e corrigidos: métricas truncadas, caixas "Mostra/Não mostra", faixa de cobertura, texto da definição das séries, percentuais de incidência (erro de ×100) e ordem do eixo jan–ago.
- Rodada de correções da revisão final:
  - **EOL:** o índice do git guardava os CSVs com LF, enquanto o manifesto registra o SHA-256 dos arquivos CRLF da cópia de trabalho; em um clone Linux a conferência falharia. `.gitattributes` passou a ter `outputs/publicacao/** -text` e a pasta foi renormalizada sem alterar conteúdo nem manifesto (SHA-256 do `manifesto.json` continua o citado na seção 2). Agora o SHA-256 dos bytes commitados (`git show HEAD:...`) confere com o manifesto nos 12 CSVs, o que o teste `test_integridade_conteudo_commitado` verifica. Exportações futuras gravam CSV e manifesto com LF.
  - **Categorias por ano** (página Volume) passam a usar `agg_cautelar.n` (contagem estadual por ano, tipo, categoria e série), que bate com a soma de `agg_categoria`; barras suprimidas são omitidas e listadas em legenda. A página não usa mais `agg_volume_jan_ago`: a comparação jan–ago vem de `agg_volume`.
  - **Tempos por mesorregião** (Território) filtram também o tipo de procedimento, sem misturar ação penal e inquérito, e a legenda informa que agregam todos os anos de ajuizamento.
  - Versões de dependências fixadas em `dashboard/requirements.txt` (`streamlit==1.67.*`, `pandas==2.3.*`, `plotly==6.9.*`); `use_container_width` trocado por `width="stretch"`.
  - Ajustes menores: download de qualidade sem `orgao_codigo`; rodapé de cobertura redigido como razão entre contagens; ordem fixa dos anos e legenda de anos sem valor na resposta cautelar; faixa "2026 parcial" na série mensal.
- Publicação: ainda não feita (ver `dashboard/README.md`).
