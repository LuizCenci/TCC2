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
