# Datajud/TJPR — coleta Bronze

O projeto implementa o piloto de coleta de metadados públicos do TJPR descrito em `docs/superpowers/specs/2026-09-22-datajud-bronze-pilot-design.md`.

## Ambiente

Use a `.venv` local:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -v
```

As respostas reais, checkpoints, logs e credenciais não são versionados. A chave deve ser fornecida somente por variável de ambiente durante uma execução autorizada.

## Coleta

```powershell
$env:DATAJUD_API_KEY = Read-Host "Cole a chave vigente obtida no CNJ"
.\.venv\Scripts\datajud-tcc.exe collect --config config/collection.example.yaml --query-kind main
Remove-Item Env:DATAJUD_API_KEY
```

O piloto limita cada partição anual a uma página de 100 registros. A consulta `diagnostic` é mantida separada da coleta temática principal.
