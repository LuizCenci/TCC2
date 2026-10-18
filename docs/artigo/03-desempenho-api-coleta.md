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
2. **Páginas maiores diluem a latência.** Com 1.000 registros, a vazão foi de cerca de 8,1 registros/s, contra cerca de 3,5 registros/s com 100: um ganho de cerca de 2,3×. A estimativa da coleta completa cai de cerca de 12 h para cerca de 5 h.
3. **A consulta não precisou mudar.** Filtro, ordenação e contagem exata continuam idênticos aos documentados em `01-parametros-da-extracao.md`. Assim, o conjunto selecionado é o mesmo; muda apenas o número de registros por requisição.

## 4. Ajustes aplicados em `config/collection.bronze.yaml`

| Parâmetro | Antes | Depois | Motivo |
|---|---:|---:|---|
| `page_size` | 100 | 1.000 | Diluir a latência fixa (§3). |
| `max_pages_per_partition` | 1.000 | 100 | Teto de segurança proporcional: o maior ano tem cerca de 25 páginas de 1.000. |
| `read_timeout_seconds` | 60 | 180 | O servidor levou 56 s para começar a responder uma página de 1.000 registros, perto do limite anterior. |

Os demais parâmetros não mudaram. A carga sobre a API **diminui**: são cerca de 145 requisições, em vez de 1.435, sempre uma por vez.
