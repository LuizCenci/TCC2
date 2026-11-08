# Dashboard de resultados

App Streamlit que exibe os agregados da camada Gold (exportação `outputs/publicacao/2026-11-05_gold-2026-11-07/`). Todos os resultados vêm exclusivamente dos metadados públicos do Datajud (CNJ), TJPR, primeiro grau, 2019–2026. O app lê somente CSVs, sem acessar banco nem API, e confere o SHA-256 de cada arquivo contra o `manifesto.json` a cada execução do aplicativo. Descrição completa: `docs/artigo/27-dashboard.md`.

## Execução local

Da raiz do repositório:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dashboard]"
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Testes: `.\.venv\Scripts\python.exe -m pytest tests/dashboard -q`.

## Publicação no Streamlit Community Cloud

A conta e o deploy são feitos pelo autor.

- Repositório: `LuizCenci/TCC2`; branch: `master`; arquivo principal: `dashboard/app.py`.
- No Cloud, escolha Python 3.12 e confira no log de build que foi usado `dashboard/requirements.txt` (versões fixadas).
- O Cloud instala `dashboard/requirements.txt` (só `streamlit`, `pandas` e `plotly`) e lê `.streamlit/config.toml` (tema lilás).
- O plano gratuito hiberna o app sem uso; acordá-lo leva cerca de 30 s. Na defesa, abrir o link antes.

## Atualização manual dos dados

1. Rodar o pipeline até a Gold (`gold-construir`, `gold-agregados`) e depois `gold-exportar`.
2. Conferir a nova pasta (12 CSVs e `manifesto.json`).
3. Commitar a nova pasta em `outputs/publicacao/`.
4. Trocar `PASTA_EXPORTACAO` em `dashboard/painel/config.py` para a nova pasta.
5. Rodar `pytest tests/dashboard` e, se algum teste citar números da exportação anterior, ajustá-lo.
6. Commit e push; o Cloud reimplanta sozinho.

## Geometria das mesorregiões

`dashboard/dados/mesorregioes_pr.geojson` é gerado uma única vez, offline, a partir da malha municipal do IBGE (`config/gold/malha_municipios_pr.geojson`) e de `config/gold/ref_municipio_pr.csv`: os municípios são dissolvidos por mesorregião e simplificados. Para regenerar (exige `shapely`, só no `.venv`):

```powershell
.\.venv\Scripts\python.exe dashboard/scripts/gerar_mesorregioes.py
```

Em produção o app lê apenas o GeoJSON, sem bibliotecas geoespaciais.
