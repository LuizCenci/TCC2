# Datajud/TJPR — coleta Bronze

O projeto implementa o piloto de coleta de metadados públicos do TJPR descrito em `docs/superpowers/specs/2026-09-22-datajud-bronze-pilot-design.md`.

## Ambiente

Use a `.venv` local:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -v
```

As respostas reais, checkpoints, logs e credenciais não são versionados.

## Chave da API

A CLI lê `DATAJUD_API_KEY` de um arquivo `.env` na raiz do projeto (ignorado pelo Git). Copie o modelo e preencha com a chave pública vigente publicada pelo CNJ:

```powershell
Copy-Item .env.example .env
# edite .env:  DATAJUD_API_KEY=<chave vigente>
```

Uma variável de ambiente `DATAJUD_API_KEY` já definida tem precedência sobre o `.env`. A chave pode mudar; consulte https://datajud-wiki.cnj.jus.br/api-publica/acesso/.

## Coleta

Com a raiz do projeto como diretório atual (o `.env` é procurado nela):

Coleta definitiva (TJPR, G1, 2019–2026, catálogo `tjpr_vcm_2026-10-18`):

```powershell
.\.venv\Scripts\datajud-tcc.exe collect --config config/collection.bronze.yaml
```

Piloto (uma página de 100 por ano):

```powershell
.\.venv\Scripts\datajud-tcc.exe collect --config config/collection.example.yaml
```

Opções: `--run-id <id>` para nomear ou retomar uma execução; `--catalog <arquivo.yaml>` para usar outro catálogo (padrão: `config/catalogs/tjpr_vcm_2026-10-18.yaml`); `--query-kind diagnostic` exige um catálogo com `classes_diagnosticas` (ex.: `pvd_cnj_2025-07-17.yaml`).

Todos os parâmetros da extração estão documentados em `docs/artigo/01-parametros-da-extracao.md`.

## Relatório

```powershell
.\.venv\Scripts\datajud-tcc.exe report --run-root <pasta da execução> [--output <arquivo.md>] [--catalog <arquivo.yaml>]
```

Para relatar execuções antigas do piloto, passe `--catalog config/catalogs/pvd_cnj_2025-07-17.yaml`: o relatório recusa um catálogo diferente do registrado no manifesto.

O piloto limita cada partição anual a uma página de 100 registros; a coleta definitiva, a 1.000 páginas por ano (teto de segurança).
