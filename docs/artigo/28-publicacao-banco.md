# Publicação do esquema e do backup do banco

Data: 10/11/2026. Status: **gerado e verificado**; restauração do backup público ainda não testada (PostgreSQL desligado no momento da geração).

## 1. Motivo

O orientador pediu que o trabalho possa ser reproduzido: SQL de criação das camadas, backup com os dados e CSVs exportados. Os CSVs já estavam em `outputs/publicacao/2026-11-05_gold-2026-11-11/`.

## 2. O que foi gerado

| Item | Origem | Destino |
|---|---|---|
| `banco/esquema_completo.sql` | `pg_restore --schema-only` sobre o backup de 09/11/2026 | Repositório |
| `tcc_datajud_publico_2026-11-07.sql.gz` (326 MB) | `pg_restore` do mesmo backup para SQL puro, com transformação dos campos identificadores | Release `dados-2026-11-07` |

SHA-256 do backup público: `a5164ffb490b346170cc79df0f0f482ae7a3bbf0192e89227635fb1031560aed`.

## 3. Tratamento dos identificadores

- O `_id` do Datajud (`silver.registro.api_id`) contém o número do processo. Verificado em uma página da Bronze de 2020: 200 de 200 `_id` contêm o `numeroProcesso`.
- `api_id`, `restrito.identificador.numero_processo` e `restrito.identificador.id_source` foram substituídos por HMAC-SHA256 com chave aleatória de 32 bytes, gerada em memória e descartada.
- Hash simples não bastaria: o número CNJ tem estrutura conhecida (sequencial, ano, órgão), e um SHA-256 sem chave poderia ser revertido por enumeração.
- A igualdade é preservada, então `gold.fato_processo` (versão mais recente por `api_id`, marcação `numero_repetido`) é reconstruída igual. O código usa `api_id` só em igualdade e ordenação (`gold/sql/10_processo.sql`).

## 4. Conferências

- Linhas transformadas: 157.844 em `silver.registro` e 157.844 em `restrito.identificador`.
- Contagens no dump: 13.674.340 movimentos, 6.888.510 complementos, 147.020 processos e 1.184.727 eventos na Gold (iguais a `17` e `24`).
- Nenhum campo inteiro de 20 dígitos nem número CNJ formatado em nenhuma tabela do dump.

## 5. Limitações

- A Bronze (JSON original) não é publicada, porque traz o número do processo; é recoletável pela API.
- `gold.fato_processo` é microdado por processo (sem número). Como a fonte é uma API pública, um registro poderia ser reencontrado cruzando datas, órgão e classe com a própria API. O backup não acrescenta informação que a API não ofereça.
- A restauração completa ainda precisa ser testada.
