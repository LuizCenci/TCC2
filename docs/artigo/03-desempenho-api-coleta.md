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
| Situação | **em andamento**; resultado final a registrar ao término |
