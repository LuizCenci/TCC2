# Anotações TCC

## Divergência entre a documentação e o formato de `dataAjuizamento`

### Documentação oficial

O glossário da API Pública do Datajud descreve `dataAjuizamento` como um campo do tipo `datetime`. Os exemplos oficiais apresentam valores em formato ISO 8601, como:

```text
2017-08-21T10:05:32.000Z
```

Fonte: [Glossário de Dados da API Pública do Datajud](https://datajud-wiki.cnj.jus.br/api-publica/glossario/).

### Observação empírica no índice público do TJPR

Na consulta ao endpoint público do TJPR, o campo foi retornado no `_source` como uma string numérica de 14 dígitos:

```text
20190402153339
```

O formato observado corresponde a:

```text
YYYYMMDDHHMMSS
```

Exemplo interpretado: `20190402153339` = 02/04/2019 às 15:33:39.

### Efeito na consulta

Uma consulta com limites ISO 8601, por exemplo:

```json
{
  "range": {
    "dataAjuizamento": {
      "gte": "2019-01-01T00:00:00.000Z",
      "lt": "2020-01-01T00:00:00.000Z"
    }
  }
}
```

retornou zero registros.

Quando os limites foram expressos no mesmo padrão numérico observado no campo:

```json
{
  "range": {
    "dataAjuizamento": {
      "gte": "20190101000000",
      "lt": "20200101000000"
    }
  }
}
```

a consulta retornou registros do TJPR, incluindo um processo ajuizado em `20190402153339`.

### Consequência metodológica

Há uma divergência entre o formato descrito na documentação geral e o formato efetivamente observado no índice público do TJPR. Essa divergência deve ser registrada como limitação e validada em amostras de diferentes anos antes da coleta definitiva.

Na implementação do pipeline:

- a camada Bronze deve preservar o valor original retornado pela API;
- a consulta deve utilizar o formato compatível com o índice do TJPR, enquanto essa característica permanecer confirmada;
- a camada Silver deve converter `YYYYMMDDHHMMSS` para um tipo de data padronizado, preservando também o valor original;
- a regra de conversão e a evidência da divergência devem ser versionadas e citadas na metodologia.

### Observação sobre a agregação temporal

Uma agregação `min`/`max` sobre o campo produziu datas interpretadas entre 1970 e 4568. Isso indica que o mecanismo de indexação pode estar tratando as strings numéricas como milissegundos desde a época Unix, e reforça a necessidade de não confiar diretamente no tipo aparente do campo sem validar o valor bruto retornado no `_source`.

Essa hipótese deve ser confirmada com novas consultas e não deve ser apresentada como característica geral da API sem verificar outros tribunais ou versões do índice.

## Estrutura real dos registros do TJPR (inventário de 24/10/2026)

Inventário de todos os campos nos 143.337 registros da coleta `bronze-20261018-9852486`. Detalhes em `docs/exemplos/exemplos_json_por_codigo.md` e `docs/exemplos/campos_api.json`. Divergências em relação ao glossário oficial:

- O órgão julgador **dentro dos movimentos** usa as chaves `codigo` e `nome`, e não `codigoOrgao` e `nomeOrgao`. Ele aparece em 99,25% dos registros.
- `movimentos[].orgaoJulgador.codigo` é **texto**, enquanto `orgaoJulgador.codigo` da capa é **inteiro**. A junção exige conversão.
- `classe.codigo` vem como texto `"-1"` (nome "Inválido") em 17 registros.
- `assuntos` vem como **lista aninhada** (lista dentro da lista) em 14 registros. A API filtra esses registros corretamente, mas a leitura precisa achatar a estrutura.
- Em 23 registros nenhum assunto tem `nome`; códigos recentes como 15174 e 15180 chegam sem nome.
- `_score` e `hits.max_score` são sempre nulos por causa da ordenação explícita.
- Não existem campos de vínculo entre processos, de local do fato ou de partes.

## Natureza dos movimentos (24/10/2026)

Hierarquia conferida no SGT/CNJ; ver `docs/artigo/evidencias/movimentos_viabilidade_20261023/hierarquia_movimentos_sgt.json`.

- Um movimento é um **ato pontual registrado** no processo (código TPU, nome, `dataHora`, órgão e complementos). **Não é uma fase com início e fim.** `dataHora` é o instante de registro do ato.
- Fases (inquérito, instrução, sentença) são **inferidas** entre marcos escolhidos por código: 26 Distribuição; 391 Recebimento da denúncia; 12750 Audiência de instrução e julgamento; 219/220/221 Julgamento; 848 Trânsito em julgado; 246 Arquivamento definitivo.
- A TPU separa os movimentos de **magistrado** (decisões, despachos, julgamentos) dos de **serventuário** (juntadas, remessas, conclusões, audiências, trânsito, arquivamento). A maior parte do volume é rotina de cartório: 581 Juntada de documento tem 2,05 milhões de ocorrências.
- Nomes compartilhados por códigos de sentido oposto: "Medida protetiva" (11423 concessão, 11424 em parte, 11425 não-concessão, 11426 revogação) e **"Denúncia" (391 recebimento, 402 rejeição)**. Classificar sempre pelo código.

## Cobertura da API pública: processos sigilosos ficam de fora (05/11/2026)

Fonte: CNJ; Instituto Avon; Consórcio Lei Maria da Penha (2022), com acesso aos dados completos do Datajud, inclusive sigilosos. Resumo e números em `docs/artigo/12-resumo-cnj-2022-medidas-protetivas.md`.

- A API pública retorna **apenas registros com `nivelSigilo = 0`**. Na coleta do TCC, 100% dos 143.337 registros têm sigilo 0.
- No relatório do CNJ, entre jan/2020 e mai/2022, o TJPR tinha **89.404 registros de MPU** (classe 1268, 1º grau). Deles, só **4.420 (4,9%) com sigilo 0** e **74.035 (≈83%) com sigilo 2**. Nacionalmente, 29,2% dos registros de MPU são públicos.
- **Convergência com a coleta:** a API pública trouxe cerca de 2.350 registros da classe 1268 por ano em 2020–2022; o relatório indica cerca de 1.800 públicos por ano no TJPR. É a mesma ordem de grandeza: **a base do TCC corresponde à fatia pública, cerca de 5%, das MPUs do TJPR.**
- Para os processos de violência doméstica em geral, o relatório conta 132.172 no TJPR em 29 meses (cerca de 55 mil por ano), contra 14–25 mil registros por ano na coleta do TCC. A cobertura dos demais procedimentos também é parcial, em grau ainda não medido.
- **Não há critério uniforme de sigilo entre os tribunais.** O principal fundamento é o Enunciado 34 do FONAVID (MPUs em segredo de justiça). A fatia pública pode não ser aleatória.
- **Consequência:** contagens do TCC descrevem o **acervo público**, não o volume real de processos. Comparações com painéis oficiais do CNJ exigem considerar o universo (todos × só públicos). Esta é a **principal limitação de cobertura** do trabalho (CLAUDE.md §4.2).

## `dataHoraUltimaAtualizacao` marca cargas em lote, não atividade processual (05/11/2026)

Teste com consultas de contagem (`size: 0`) no recorte temático G1. Evidências em `docs/artigo/evidencias/teste_ultima_atualizacao_20261105/`; scripts `teste_ultima_atualizacao*.py`.

- O filtro `range` em `dataHoraUltimaAtualizacao` **funciona com datas ISO 8601** (`2026-10-01T00:00:00.000Z` ou `2026-10-01`; mesmo resultado). Com o formato `YYYYMMDDHHMMSS` de `dataAjuizamento` retorna **zero**: os dois campos de data têm formatos diferentes no índice.
- Os valores se concentram em **poucos dias**: 01/09/2026 (112.284 dos 147.548 registros do recorte), 14–15/09 e 28/09 (≈12 mil), 05/10/2026 (14.358, todos entre 15h24 e 18h00), e lotes mensais menores (cerca de 500–1.500) antes disso. `@timestamp` acompanha o mesmo padrão.
- Interpretação: o campo registra quando o **tribunal reenviou o registro ao Datajud**, não quando houve movimento no processo. Isso confirma o CLAUDE.md §4.7: atualização do índice não equivale a evento judicial.
- **Uso possível:** marca d'água para coleta incremental. "Registros com `dataHoraUltimaAtualizacao` posterior à última carga coletada" traz processos novos **e antigos reenviados**: dos 14.875 atualizados em outubro/2026, 9.085 tinham ajuizamento entre 2019 e 2025. Custo: cada lote vem inteiro, e recargas completas como a de 01/09 trazem quase toda a base.
- Entre 18/10 e 05/11/2026 o recorte temático G1 (2019–2026) passou de 143.337 para 147.548 registros.
