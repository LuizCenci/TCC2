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

```powershell
.\.venv\Scripts\datajud-tcc.exe collect --config config/collection.example.yaml --query-kind main
```

Opções: `--query-kind diagnostic` para a consulta diagnóstica; `--run-id <id>` para nomear ou retomar uma execução.

## Relatório

```powershell
.\.venv\Scripts\datajud-tcc.exe report --run-root <pasta da execução> [--output <arquivo.md>]
```

O piloto limita cada partição anual a uma página de 100 registros. A consulta `diagnostic` é mantida separada da coleta temática principal.
