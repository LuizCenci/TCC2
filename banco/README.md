# Banco de dados

Esquema e backup do banco PostgreSQL usado no TCC (versão de regras `gold-2026-11-11`).

## Arquivos

| Arquivo | Onde | Conteúdo |
|---|---|---|
| `esquema_completo.sql` | Esta pasta | DDL de todas as camadas no banco: `controle` (execuções e páginas da Bronze), `silver`, `restrito`, `ref` e `gold`, mais a extensão PostGIS. Sem dados. |
| `tcc_datajud_publico_2026-11-07.sql.gz` | Release [`dados-2026-11-07`](https://github.com/LuizCenci/TCC2/releases/tag/dados-2026-11-07) | Esquema + dados de todas as tabelas (SQL puro comprimido, cerca de 330 MB). |

A camada Bronze não tem SQL: são os arquivos JSON originais da API, que não são publicados porque trazem o número do processo. Eles podem ser recoletados com `datajud-tcc collect` (ver `readme.md` na raiz).

SHA-256 do backup público: `a5164ffb490b346170cc79df0f0f482ae7a3bbf0192e89227635fb1031560aed`.

## O que foi alterado no backup público

Os campos que contêm o número do processo foram substituídos por HMAC-SHA256 com chave aleatória descartada após a geração:

- `silver.registro.api_id` (o `_id` do Datajud embute o número);
- `restrito.identificador.numero_processo` e `restrito.identificador.id_source`.

Valores iguais continuam iguais, então a Gold reconstruída a partir da Silver dá o mesmo resultado (inclusive a marcação de números repetidos). Sem a chave, não é possível recuperar o número por enumeração. Os demais dados estão como no banco original.

## Restaurar

Requer PostgreSQL 16 com PostGIS instalado.

```bash
createdb -U postgres tcc_datajud
gunzip -c tcc_datajud_publico_2026-11-07.sql.gz | psql -U postgres -d tcc_datajud
```

Para criar só a estrutura vazia:

```bash
psql -U postgres -d tcc_datajud -f banco/esquema_completo.sql
```

Depois da restauração, a Gold pode ser reconstruída com `datajud-tcc gold-construir` e os agregados com os comandos descritos na seção Gold do `readme.md`.
