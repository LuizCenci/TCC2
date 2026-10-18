# Desempenho da API Datajud e ajuste do tamanho de página

Data: 18/10/2026, entre 01:03 e 01:16 (horário local). Status: **verificado**. Evidências em `evidencias/desempenho_api_20261018/`; scripts `perf.py`, `perf2.py` e `perf3.py` em `evidencias/scripts/`.

## 1. Problema observado

A primeira execução da coleta definitiva (`run_id = bronze-20261018-24c258c`, `page_size = 100`) gastou de **16 a 42 s de processamento no servidor por página** (`took`). A média foi de 26,7 s e a mediana de 26,2 s, em 26 páginas. Nesse ritmo, as cerca de 1.435 páginas levariam aproximadamente 12 horas. As respostas eram pequenas (cerca de 200 KB comprimidas por página), o que mostra que o gargalo estava no servidor, e não na transferência.

A execução foi **interrompida intencionalmente** após 26 páginas de 2019 (2.600 registros). Seus arquivos foram preservados em `work/bronze/datajud/tjpr/collected_at=2026-10-18/run_id=bronze-20261018-24c258c/`, mas ela **não é a coleta usada na pesquisa**. O manifesto ficou com `status = running` porque o processo foi encerrado externamente.

## 2. Testes de isolamento

Os testes foram feitos com requisições isoladas, partindo da consulta da página 2 de 2019 (com `search_after`). As medições ocorreram enquanto a coleta ainda rodava, com uma requisição concorrente.

| Variante | `took` (s) | Tempo total (s) | Registros |
|---|---:|---:|---:|
| Consulta original (100, contagem exata, ordenação por `id.keyword`) | 27,3 | 28,2 | 100 |
| Sem `track_total_hits` | 25,8 | 26,5 | 100 |
| Sem `_source` (só ordenação) | 32,5 | 33,0 | 100 |
| Sem ordenação | 23,9 | 24,7 | 100 |
| Ordenação `_doc` | 21,9 | 22,6 | 100 |
| Sem filtro de data | 32,3 | 33,0 | 100 |
| Só data e grau (sem filtro temático) | 26,0 | 26,7 | 100 |
| Só grau | 21,9 | 22,6 | 100 |
| **1.000 por página**, sem contagem exata | 56,1 | 123,0 | 1.000 |

## 3. Conclusões

1. **Latência fixa de cerca de 22–33 s por consulta.** Ela aparece mesmo na consulta mais simples (só grau) e não é explicada pela contagem exata, pela ordenação, pela leitura do `_source`, pelo filtro de data nem pelo filtro temático. Provavelmente é carga ou configuração do servidor público (hipótese, sem acesso à infraestrutura do CNJ).
2. **Páginas maiores diluem a latência.** Com 1.000 registros, a vazão foi de cerca de 8,1 registros/s, contra cerca de 3,5 registros/s com 100: um ganho de cerca de 2,3×. Essa estimativa (cerca de 5 h) foi revista na §5, depois do corte de 60 s do gateway.
3. **A consulta não precisou mudar.** Filtro, ordenação e contagem exata continuam idênticos aos documentados em `01-parametros-da-extracao.md`. Assim, o conjunto selecionado é o mesmo; muda apenas o número de registros por requisição.

## 4. Segunda tentativa: corte de 60 s no gateway (HTTP 504)

A execução `bronze-20261018-12748ce`, com `page_size = 1.000`, recebeu **HTTP 504 em três tentativas consecutivas** na primeira página de 2019, cada uma após exatos cerca de 60 s (01:16:58–01:20:02). Ela terminou com `status = failed` e **nenhuma página gravada**. O intervalo constante indica que o gateway da API pública **interrompe consultas que passam de 60 s**. A página de 1.000 com contagem exata ultrapassa esse limite; no teste anterior, sem contagem, ela havia levado 56 s.

Nova medição, primeira página de 2019 com a consulta completa (`track_total_hits: true`), às 01:21–01:22:

| `size` | `took` (s) | Tempo total (s) | Resposta (descomprimida) |
|---:|---:|---:|---:|
| 500 | 55,7 | 56,6 | 16,7 MB |
| 250 | 46,2 | 47,0 | 8,6 MB |

O custo cresce com o tamanho da página, porque o servidor precisa ler o `_source` completo, que inclui os movimentos. Com 500 não sobra margem sob os 60 s. Como os tempos com 100 registros variaram entre 16 e 42 s, **200 registros por página** (cerca de 40 s estimados) foi escolhido para equilibrar vazão e risco de 504.

## 5. Parâmetros finais em `config/collection.bronze.yaml`

| Parâmetro | Piloto / 1ª execução | 2ª execução (falhou) | **Final** | Motivo |
|---|---:|---:|---:|---|
| `page_size` | 100 | 1.000 | **200** | Diluir a latência fixa sem ultrapassar o corte de 60 s do gateway. |
| `max_pages_per_partition` | 1.000 | 100 | **300** | Teto de segurança: o maior ano tem cerca de 125 páginas de 200. |
| `read_timeout_seconds` | 60 | 180 | **90** | Acima do corte do gateway, para que o 504 do servidor seja o sinal de falha. |

Os demais parâmetros e a consulta (filtro, ordenação, contagem exata) **não mudaram**.

**Retomada automática limitada.** Se uma partição falhar depois das 3 tentativas do cliente (por exemplo, por 504 persistente), a **mesma execução** é retomada a partir do checkpoint do manifesto, no máximo 5 vezes, com 2 minutos de pausa entre elas. Páginas já gravadas são verificadas por SHA-256 e não são baixadas de novo. Cada retomada fica registrada no log da execução.

Estimativa: cerca de 720 requisições e de 6 a 8 h de coleta, sempre com uma requisição por vez.

## 6. Execução definitiva

| Item | Valor |
|---|---|
| `run_id` | `bronze-20261018-9852486` (commit `9852486`) |
| Início | 18/10/2026 01:23:33 |
| Primeiras páginas (2019) | cerca de 21–37 s por página de 200; total exato de 2019 = 24.956 (`eq`), igual à validação prévia |
| Log | `work/logs/bronze-20261018-9852486.log` |
| 2019 | completo às 02:36:57: 125 páginas, **24.956 de 24.956** registros |
| Situação | **concluída** às 07:19:21, com 143.337 registros e todos os anos completos; ver `06-resultado-coleta-bronze.md` |

### 6.1 Limite de requisições (HTTP 429) na virada da hora

Houve HTTP 429 **exatamente às 02:00:14 e às 03:00:00**. Às 02:00 a nova tentativa funcionou; a falha seguinte, às 02:01, foi um 504 isolado, também superado. Às 03:00 as três tentativas do cliente (pausas de 1 s e 2 s, porque a resposta não trazia `Retry-After`) se esgotaram. O ano de 2020 terminou com `RateLimitError`. O script de retomada esperou 2 min e, às 03:02:03, retomou a **mesma execução** a partir da página 51 de 2020, sem baixar de novo páginas já gravadas.

Hipótese, não confirmada: a API aplica uma cota por janela horária ou faz manutenção no início de cada hora. Se o padrão se repetir, as retomadas previstas (5) devem bastar para as horas restantes. Caso se esgotem, a coleta é retomada manualmente com `bash scripts/coletar_bronze.sh bronze-20261018-9852486`.

### 6.2 Computador acordado durante a coleta

Para evitar que a suspensão por inatividade interrompa a coleta, `scripts/manter_acordado.ps1` chama `SetThreadExecutionState` do Windows (`ES_CONTINUOUS | ES_SYSTEM_REQUIRED`) enquanto o log não registrar o fim da execução. Ele **não altera** as configurações de energia e libera o pedido ao terminar. Isso não impede a suspensão por fechamento da tampa ou por comando manual; nesses casos, a retomada do checkpoint continua válida.

**Verificado pelo autor** com `powercfg /requests` (prompt elevado), em 18/10/2026: pedido `SYSTEM` ativo para `powershell.exe` (o script) e pedido `EXECUÇÃO` para o aplicativo Claude; nenhum pedido em `DISPLAY` (a tela pode apagar, o que não afeta a coleta).

## 7. Paralelismo: avaliado, não adotado — proposta para implementação futura

Status: **avaliação e proposta** (18/10/2026). Nada disto foi implementado ou medido. A coleta definitiva (§6) usou **uma requisição por vez**.

### 7.1 Por que a coleta definitiva foi sequencial

1. **O limite de requisições apareceu mesmo sem concorrência.** Houve cinco HTTP 429, e um deles interrompeu uma partição (§6.1). Requisições simultâneas tendem a atingir o limite com mais frequência ou a provocar um bloqueio temporário da chave, que é compartilhada por todos os usuários da API pública.
2. **A natureza da latência é desconhecida.** A espera fixa de cerca de 22–33 s (§3) pode ser **fila**, e nesse caso o paralelismo reduziria o tempo total. Pode também ser **processamento**, e então requisições simultâneas ficariam individualmente mais lentas e o ganho diminuiria. Só a medição separa as duas hipóteses.
3. **Conduta.** CLAUDE.md §8 orienta não sobrecarregar a infraestrutura do CNJ. A coleta sequencial é a posição mais conservadora e fácil de justificar no artigo.
4. **Custo e risco.** O manifesto e o checkpoint atuais foram desenhados para um único processo. O tempo de coleta (cerca de 6 h, com retomada automática) foi aceitável para uma coleta única.

### 7.2 Hipótese a testar

> **H1:** uma requisição concorrente por ano (até 8 workers), com controle global de ritmo, reduz o tempo total da coleta sem aumentar de forma relevante a taxa de HTTP 429/504 e sem alterar o conjunto coletado.

Cada ano é uma partição independente, com consulta e cursor `search_after` próprios. A paginação **dentro** de um ano continua sequencial, porque cada página depende do cursor da anterior. O ganho máximo teórico é limitado pelo ano mais longo: 2019, com cerca de 125 páginas, ou aproximadamente 1 h a 1 h 15 no ritmo observado, contra cerca de 6 h sequenciais. Isso só vale se a latência for fila (§7.1, item 2).

Variante para equilibrar a carga, caso os anos fiquem desiguais: subdividir cada ano em meses (filtro `dataAjuizamento` mensal) e distribuir as partições numa fila de trabalho.

### 7.3 Desenho proposto

| Componente | Proposta |
|---|---|
| Concorrência | `ThreadPoolExecutor` com `max_workers` configurável (`parallel_partitions` no YAML; padrão 1 = comportamento atual). Uma partição (ano) por tarefa. |
| Cliente HTTP | Um `requests.Session` **por thread**, porque `Session` não é garantidamente seguro entre threads. |
| Ritmo global | Limitador compartilhado (*token bucket*) com teto de requisições em andamento e intervalo mínimo entre inícios de requisição, configuráveis. |
| Reação a 429 | **Pausa global:** um 429 suspende todos os workers pelo `Retry-After` (ou recuo exponencial compartilhado) e reduz temporariamente a concorrência efetiva (por exemplo, pela metade), restaurando-a de forma gradual. |
| Janela horária | Opcional: evitar iniciar requisições entre hh:59:30 e hh:00:30, onde os 429 se concentraram (§6.1), se o padrão se confirmar. |
| Manifesto | Escrita protegida por `threading.Lock`, ou um arquivo de estado **por partição** (`partitions/year=AAAA.json`) consolidado ao final, que elimina a disputa pelo manifesto. |
| Bronze | Sem mudança: os caminhos já são separados por ano e as escritas são idempotentes, com comparação de conteúdo. |
| Falhas | A falha de um ano não cancela os demais; o status final segue as regras atuais (`complete`, `failed`, `limited`). A retomada continua por checkpoint de cada partição. |
| Logs | Cada linha identifica o ano e o worker; métricas por requisição (`took`, tempo total, status HTTP). |

### 7.4 Protocolo de comparação

Para que a comparação seja válida e possa ser relatada:

1. **Mesmo recorte:** mesmo catálogo, configuração e consulta. Usar um subconjunto, por exemplo os 20 primeiros páginas de cada ano, para não repetir a coleta inteira.
2. **Tratamentos:** 1, 2, 4 e 8 workers, intercalados e repetidos (ao menos 2 vezes cada), em horários semelhantes, para reduzir o efeito da carga variável do servidor.
3. **Métricas:** tempo total; registros por segundo; distribuição de `took` (mediana e percentil 90); número de 429 e 504; retomadas.
4. **Critério de equivalência:** cada tratamento deve produzir **o mesmo conjunto de `_id` e as mesmas contagens por ano** que a coleta sequencial (`06-resultado-coleta-bronze.md`).
5. **Critério de adoção:** adotar concorrência apenas se o ganho de tempo for relevante **e** a taxa de 429 não crescer de forma material. Caso contrário, manter a coleta sequencial e registrar o resultado como achado sobre a API.
6. **Limite de conduta:** nunca mais de 8 requisições simultâneas, sem rotação de chave ou identidade, e interromper o experimento se surgirem bloqueios ou 429 persistentes.

### 7.5 Uso no artigo

Se o experimento for feito, ele pode compor uma seção curta de **avaliação do pipeline** (CLAUDE.md §12): tempo de coleta sequencial *versus* concorrente, custo em limites de requisição e equivalência dos dados coletados. Se não for feito, este registro justifica a escolha da coleta sequencial.
