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
