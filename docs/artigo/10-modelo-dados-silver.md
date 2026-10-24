# Modelo de dados da camada Silver — proposta

Data: 23/10/2026. Status: **proposta de desenho**, ainda não implementada. Baseia-se nos achados de `06`, `07` e `08` e no CLAUDE.md §8–§13. As escolhas marcadas como "a decidir" dependem do autor.

## 1. Princípios

1. **Original separado de derivado.** As tabelas `silver.*` guardam o que a API trouxe, só tipado e normalizado. Tudo o que o projeto infere (tipo de procedimento, grupo, categorias, eventos, flags) fica em tabelas `deriv.*`, **ligadas a uma versão de regras**. Mudar uma regra cria uma nova versão; nada é sobrescrito em silêncio.
2. **Uma tabela por relação de cardinalidade diferente.** Assuntos, movimentos e complementos ficam separados, para evitar o produto cartesiano (3 assuntos × 20 movimentos = 60 linhas, CLAUDE.md §9).
3. **Rastreabilidade até a Bronze.** Cada registro aponta para a execução, o ano e a página de origem. O SHA-256 da página permite verificar o dado.
4. **Carga idempotente.** A chave natural é `(run_id, api_id)`. Recarregar a mesma execução não duplica nada.
5. **Valores originais preservados ao lado dos convertidos:** datas como texto e como `timestamp`, nomes como a API trouxe.
6. **Privacidade por camada.** O número do processo fica numa tabela de acesso restrito; o restante usa uma chave substituta (CLAUDE.md §13).
7. **Referências versionadas e com fonte:** TPU (SGT), catálogo temático, comarcas e municípios, com data de consulta e vigência.

## 2. Esquemas

| Esquema | Conteúdo |
|---|---|
| `controle` | Execuções de coleta, páginas da Bronze, cargas na Silver |
| `silver` | Dados originais normalizados |
| `ref` | Tabelas de referência: TPU, catálogo, órgãos, territórios |
| `deriv` | Classificações e eventos derivados por regra versionada |
| `restrito` | Identificadores processuais (acesso limitado) |
| `gold` | Agregações e visões para o dashboard (fora deste documento) |

## 3. Diagrama — núcleo (dados originais)

```mermaid
erDiagram
    controle_execucao_coleta ||--o{ controle_pagina_bronze : "gera"
    controle_pagina_bronze ||--o{ silver_registro : "contém"
    silver_registro ||--|| restrito_identificador : "identificado por"
    silver_registro ||--o{ silver_registro_assunto : "tem"
    silver_registro ||--o{ silver_movimento : "tem"
    silver_movimento ||--o{ silver_complemento_movimento : "tem"
    ref_tpu_classe ||--o{ silver_registro : "classe atual"
    ref_tpu_assunto ||--o{ silver_registro_assunto : "codifica"
    ref_tpu_movimento ||--o{ silver_movimento : "codifica"
    ref_orgao_julgador ||--o{ silver_registro : "órgão atual"
    ref_orgao_julgador ||--o{ silver_movimento : "órgão do movimento"

    controle_execucao_coleta {
        text run_id PK
        text catalogo_versao
        char64 catalogo_sha256
        char64 config_hash
        text commit_codigo
        timestamptz iniciada_em
        timestamptz concluida_em
        text status
    }
    controle_pagina_bronze {
        text run_id PK,FK
        smallint ano PK
        int pagina PK
        char64 sha256
        int n_registros
        int total_api
    }
    silver_registro {
        bigint registro_id PK
        text run_id FK
        text api_id UK "com run_id"
        smallint ano_particao
        int pagina
        text grau
        int classe_codigo FK
        int orgao_codigo FK
        int municipio_sede_ibge
        text data_ajuizamento_original
        timestamp data_ajuizamento
        timestamptz data_ultima_atualizacao
        timestamptz indexado_em
        smallint nivel_sigilo
        smallint sistema_codigo
        smallint formato_codigo
        int n_movimentos
        char64 hash_source
    }
    restrito_identificador {
        bigint registro_id PK,FK
        text numero_processo
        smallint ano_numero_cnj
        text chave_pseudonima
    }
    silver_registro_assunto {
        bigint registro_id PK,FK
        int assunto_codigo PK,FK
        text nome_original
        smallint posicao
        bool veio_aninhado
    }
    silver_movimento {
        bigint movimento_id PK
        bigint registro_id FK
        int codigo FK
        text nome_original
        timestamptz data_hora
        int dias_desde_ajuizamento
        text orgao_codigo_original
        int orgao_codigo FK
        int ordem_original
        int ordem_cronologica
    }
    silver_complemento_movimento {
        bigint movimento_id PK,FK
        smallint ordem PK
        int codigo
        text descricao
        int valor
        text nome
    }
```

## 4. Diagrama — referências e derivados

```mermaid
erDiagram
    ref_tpu_assunto ||--o{ ref_tpu_assunto : "pai"
    ref_tpu_movimento ||--o{ ref_tpu_movimento : "pai"
    ref_versao_regras ||--o{ ref_catalogo_tematico : "define"
    ref_versao_regras ||--o{ ref_classe_tipo_procedimento : "define"
    ref_versao_regras ||--o{ ref_regra_evento : "define"
    ref_versao_regras ||--o{ ref_categoria_codigo : "define"
    ref_municipio ||--o{ ref_comarca_municipio : "atendido por"
    ref_comarca ||--o{ ref_comarca_municipio : "abrange"
    ref_comarca ||--o{ ref_orgao_julgador : "sedia"
    ref_regiao ||--o{ ref_municipio : "agrupa"

    silver_registro ||--o{ deriv_classificacao : "classificado"
    ref_versao_regras ||--o{ deriv_classificacao : "versão"
    silver_registro ||--o{ deriv_registro_categoria : "categorias"
    silver_registro ||--o{ deriv_evento : "eventos"
    silver_movimento ||--o{ deriv_evento : "origem"
    silver_registro ||--o{ deriv_tempo : "tempos"
    silver_registro ||--o{ deriv_flag_qualidade : "flags"

    ref_versao_regras {
        text versao PK
        date criada_em
        text descricao
        text documento
    }
    ref_tpu_assunto {
        int codigo PK
        text nome
        int pai_codigo FK
        text caminho
        text fonte
        date consultado_em
    }
    ref_tpu_movimento {
        int codigo PK
        text nome
        int pai_codigo FK
        text caminho
        date consultado_em
    }
    ref_catalogo_tematico {
        text versao PK,FK
        text tipo PK "assunto ou classe"
        int codigo PK
        text grupo "nucleo, especifica, ambigua, secundaria, marcador"
        text justificativa
    }
    ref_categoria_codigo {
        text versao PK,FK
        text categoria PK
        int assunto_codigo PK
        bool so_serie_ampliada
    }
    ref_classe_tipo_procedimento {
        text versao PK,FK
        int classe_codigo PK
        text tipo "principal, medida_protetiva, incidente, carta, civel, outros"
    }
    ref_regra_evento {
        text versao PK,FK
        int movimento_codigo PK
        text evento "decisao_mpu_concessao, arquivamento_definitivo, julgamento..."
    }
    ref_orgao_julgador {
        int orgao_codigo PK
        text nome
        int municipio_sede_ibge FK
        int comarca_id FK
        text tipo_unidade "JVDFM, criminal, juizo_unico..."
    }
    ref_comarca {
        int comarca_id PK
        text nome
        int sede_ibge
        text entrancia
        date vigente_desde
        date vigente_ate
    }
    ref_comarca_municipio {
        int comarca_id PK,FK
        int municipio_ibge PK,FK
        date vigente_desde PK
        date vigente_ate
        text fonte
    }
    ref_municipio {
        int municipio_ibge PK
        text nome
        int regiao_imediata FK
        int regiao_intermediaria
    }
    ref_regiao {
        int regiao_codigo PK
        text nome
        text tipo
        text fonte
    }
    deriv_classificacao {
        bigint registro_id PK,FK
        text versao PK,FK
        text tipo_procedimento
        text grupo_inclusao
        bool serie_estrita
        bool serie_ampliada
        bool em_analise "2019-2025"
        bool registro_canonico "dedup por numero"
    }
    deriv_registro_categoria {
        bigint registro_id PK,FK
        text versao PK
        text categoria PK
        text motivo
    }
    deriv_evento {
        bigint registro_id FK
        text versao
        text evento
        bigint movimento_id FK
        int dias_desde_ajuizamento
    }
    deriv_tempo {
        bigint registro_id PK,FK
        text versao PK
        int dias_ate_decisao_mpu
        text decisao_mpu
        int dias_ate_fim
        text status_observacao "encerrado, censurado, sem_dados"
        int dias_acompanhamento
    }
    deriv_flag_qualidade {
        bigint registro_id PK,FK
        text versao PK
        text flag PK
        text detalhe
    }
```

## 5. Dicionário resumido e motivos

### Dados originais (`silver`, `restrito`, `controle`)

| Tabela | Grão (uma linha por…) | Volume estimado | Motivo / achado que justifica |
|---|---|---:|---|
| `controle.execucao_coleta` | execução | poucas | Vincula cada dado ao catálogo, à configuração e ao commit (`06`) |
| `controle.pagina_bronze` | página da Bronze | 721 | Rastreabilidade e verificação por SHA-256 |
| `silver.registro` | registro da API (`_id`) | 143 mil | Unidade técnica; classe e órgão são os **atuais** (`07` §3, CLAUDE.md §4.6) |
| `restrito.identificador` | registro | 143 mil | Número do processo isolado (privacidade); `ano_numero_cnj` permite checagens como a de `08` §7.2 |
| `silver.registro_assunto` | registro × assunto | ~270 mil | Multirrótulo (1,9 por registro); `veio_aninhado` marca os 14 registros com lista aninhada (`07` §1) |
| `silver.movimento` | movimento | ~13,5 mi | Ordem original **e** cronológica (CLAUDE.md §7); órgão do movimento original (texto) e normalizado (inteiro) |
| `silver.complemento_movimento` | complemento | ~6–9 mi | Medidas e beneficiário da MPU (`07` §5); motivo da redistribuição |

### Referências (`ref`)

| Tabela | Conteúdo | Fonte |
|---|---|---|
| `tpu_assunto`, `tpu_classe`, `tpu_movimento` | Nome oficial e hierarquia (autorreferência ao pai) | SGT/CNJ (`evidencias/sgt_tpu_*`, `movimentos_viabilidade_*`) |
| `versao_regras` | Cada versão das regras de classificação | Documento que a justifica |
| `catalogo_tematico` | Códigos e grupos | `config/catalogs/tjpr_vcm_2026-10-18.yaml` |
| `categoria_codigo` | Códigos → categorias analíticas | `07` §8 (a decidir) |
| `classe_tipo_procedimento` | Classe → tipo de procedimento | `07` §2 |
| `regra_evento` | Código de movimento → evento | `07` §5, `08` §2 |
| `orgao_julgador` | 297 órgãos; sede; comarca; tipo de unidade | API + classificação manual do nome |
| `comarca`, `comarca_municipio` | Território atendido, com **vigência** | TJPR (a obter, `09` §4.A) |
| `municipio`, `regiao` | Nomes e regiões imediatas/intermediárias | IBGE (versão a registrar) |

### Derivados (`deriv`), sempre por `versao`

| Tabela | Conteúdo | Origem da regra |
|---|---|---|
| `classificacao` | Tipo de procedimento, grupo de inclusão, série estrita/ampliada, `em_analise` (2019–2025), registro canônico | `01`, `07` |
| `registro_categoria` | Categorias multirrótulo com motivo | `07` §8 |
| `evento` | Eventos identificados por código: decisão de MPU (concessão, em parte, não-concessão), revogação, prorrogação, julgamento, trânsito, arquivamento definitivo, reabertura | `07` §5, `08` §2 |
| `tempo` | Primeira decisão de MPU, fim, `status_observacao` (encerrado/censurado/sem dados), tempo de acompanhamento | `08` §4; campos sugeridos no CLAUDE.md §11 |
| `flag_qualidade` | Ver §6 | `07`, `08` |

## 6. Flags de qualidade previstas

| Flag | Regra | Achado |
|---|---|---|
| `marcador_nao_mulher` | assunto 12195 ou 12197 | `07` §1 |
| `marcador_crianca` | assunto 15174 ou 15180 | `07` §1 |
| `infracional_em_classe_criminal` | código infracional em classe criminal comum | `07` §1 |
| `assunto_aninhado` | `assuntos` em lista aninhada (14 registros) | `07` §1; `docs/exemplos/campos_api.json` |
| `numero_multiplo` | número de processo com mais de um registro | `07` §3 (70 números) |
| `inicio_documento` | primeiro movimento = 581 "Documento" | `08` §7.2 |
| `carta_pico_2019_2020` | carta precatória entre jul/2019 e dez/2020 | `08` §7.1 |
| `movimento_antes_ajuizamento` | algum movimento anterior ao ajuizamento | `08` §1 (24 casos) |
| `assunto_sem_nome` | nome ausente na API (15174, 15180) | `07` §1 |
| `classe_invalida` | `classe.codigo` = texto `"-1"` (17 registros) | `docs/exemplos/campos_api.json` |

## 7. Fluxo de carga

```text
Bronze (páginas .json.gz)
  → 1. controle: registra a execução e as páginas (verifica SHA-256)
  → 2. silver: insere registros, assuntos, movimentos, complementos
        (chave (run_id, api_id); conversão de datas; normalização de tipos)
  → 3. ref: carrega TPU (SGT), catálogo, tipos de classe, regras de evento, territórios
  → 4. deriv: para uma versão de regras, recalcula classificação, categorias,
        eventos, tempos e flags (DELETE + INSERT daquela versão)
  → 5. testes de consistência (contagens = Bronze; sem duplicatas; somas por ano)
```

O passo 4 é o único que se repete quando as regras mudam; os passos 1–3 só se repetem com uma nova coleta.

## 8. Decisões em aberto

1. **SGBD:** PostgreSQL, conforme o PDF e o CLAUDE.md §9. Com cerca de 13,5 milhões de movimentos, cabe bem numa instalação local. Alternativa mais leve para o TCC: DuckDB, sem servidor, lendo direto os arquivos. *(a decidir)*
2. **Dados de 2026:** carregar na Silver com `em_analise = false` (recomendado), ou não carregar.
3. **Deduplicação:** critério para escolher o registro canônico entre os 70 números com mais de um registro (por exemplo, a atualização mais recente).
4. **Chave pseudônima:** HMAC do número com segredo fora do repositório, se o dashboard precisar de algum identificador estável. Hash não equivale a anonimização (CLAUDE.md §13).
5. **Categorias analíticas e série estrita × ampliada:** `07` §8.
6. **Fonte territorial:** tabela de comarcas do TJPR e versão das regiões do IBGE (`09`).
