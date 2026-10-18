# SINAN Violência — exploração do Paraná, 2023–2024

Relatório exploratório. **Não é decisão de escopo**: a incorporação do SINAN ao TCC depende de alinhamento com o orientador (CLAUDE.md, seções 1 e 18).

## 1. Procedência

| Item | Valor |
|---|---|
| Fonte | DATASUS, FTP público — `ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/DADOS/FINAIS/` |
| Arquivos | `VIOLBR23.dbc` (34.888.592 bytes), `VIOLBR24.dbc` (46.449.962 bytes) — dados **finais** |
| SHA-256 | 23: `45c042da…2664f635` · 24: `471c7a24…c2b649` (completos em §8) |
| Data do download | 2026-10-16T00:19:55Z |
| Documentação | `SINAN/DOCS/Docs_TAB_SINAN.zip` → `VIOLEN_DIC_DADOS.pdf`, `VIOLEN_FICHA.pdf` (baixado em 17/10/2026) |
| Leitura | `pyreaddbc` (DBC→DBF) + `dbfread`, encoding latin-1 |
| Script | `docs/artigo/evidencias/scripts/explorar_sinan_pr.py` |
| Armazenamento | brutos em `work/sinan/` (≈ 730 MB, adicionado ao `.gitignore`) |

Também existe `PRELIM/VIOLBR25.dbc` (preliminar, não usado). A série final disponível vai até 2024.

## 2. Unidade e recorte

- **Unidade: notificação** de violência interpessoal ou autoprovocada feita por serviço de saúde (agravo `Y09`). Não é vítima, nem ocorrência, nem processo. O campo `NDUPLIC` está vazio, então **não há como identificar a mesma pessoa notificada mais de uma vez**.
- Recorte PR: `SG_UF_NOT = 41` (notificada no PR). Os recortes por residência (`SG_UF`) e ocorrência (`SG_UF_OCOR`) diferem em menos de 0,2%.
- Recorte principal deste relatório: `CS_SEXO = F` e `LES_AUTOP ≠ 1`, isto é, **excluindo lesão autoprovocada**. Registros com `LES_AUTOP` = 9 ou vazio permanecem (≈ 3,7% das notificações de sexo F).

| Ano de notificação | Todas (PR) | Sexo F | F, exceto autoprovocada | F ≥ 18 anos, exceto autoprovocada |
|---|---:|---:|---:|---:|
| 2023 | 50.082 | 34.241 | 24.702 | 13.940 |
| 2024 | 55.876 | 37.803 | 28.623 | 16.254 |

Achado importante: **43% do recorte "F, exceto autoprovocada" são meninas de 0 a 17 anos** (23.131 de 53.325), e boa parte desses casos envolve negligência ou violência intrafamiliar. Para dialogar com a Lei Maria da Penha e com o Datajud, o recorte natural é **mulheres ≥ 18 anos**. Essa escolha ainda precisa ser decidida.

O ano do arquivo é o **ano de notificação**. A data de ocorrência (`DT_OCOR`) cai em ano anterior em cerca de 2% dos casos.

## 3. Preenchimento dos campos (F, exceto autoprovocada; n = 53.325)

"Ignorado" significa código 9/99, que pode existir mesmo com o campo preenchido.

| Campo | Significado (dicionário) | Preenchido | Ignorado |
|---|---|---:|---:|
| `DT_OCOR` | data da ocorrência | 100% | — |
| `ID_MN_OCOR` | município de ocorrência (IBGE, 6 dígitos) | 99,99% | — |
| `ID_MN_RESI` | município de residência | 100% | — |
| `NU_IDADE_N` | idade (codificada: 4xxx = anos) | 100% | — |
| `CS_RACA` | raça/cor | 99,4% | 9,2% |
| `CS_ESCOL_N` | escolaridade | 96,4% | 21,4% |
| `LOCAL_OCOR` | local de ocorrência | 100% | 9,9% |
| `OUT_VEZES` | violência de repetição | 99,6% | 18,2% |
| `AUTOR_SEXO` | sexo do provável autor | 99,9% | 4,3% |
| `AUTOR_ALCO` | suspeita de uso de álcool pelo autor | 99,5% | 28,2% |
| `REL_*` | vínculo com o autor (um campo sim/não por vínculo) | 99,9% | ≈ 2,5% |
| `VIOL_*` | tipo de violência (um campo sim/não por tipo) | 100% | ≈ 1–2% |
| `VIOL_MOTIV` | motivação (sexismo, racismo…) | 100% | 54,2% (inclui 88 "não se aplica") |
| `HORA_OCOR` | hora | 42,4% | — |
| `ATEND_MULH`, `DELEG_MULH`, `MPU`… | encaminhamentos | 99,9% | ≈ 2,3% |
| `ENC_*` (ficha antiga), `CLASSI_FIN`, `EVOLUCAO`, `NDUPLIC` | — | **0%** | — |

Em resumo, a geografia e as variáveis de perfil e de vínculo estão muito bem preenchidas. As exceções são a motivação e o álcool, com muitos ignorados.

### Armadilhas de dicionário (verificadas no `VIOLEN_DIC_DADOS.pdf`)

- **`MPU` é encaminhamento ao Ministério Público, não medida protetiva de urgência.** O SINAN **não** registra concessão de medida protetiva.
- **`CICL_VID` é o ciclo de vida do provável autor**, não da vítima.
- `VIOL_MOTIV`: 01 sexismo, 02 homo/lesbo/bi/transfobia, 03 racismo, …, 09 outros, 88 não se aplica, 99 ignorado.
- Os campos `ENC_*` pertencem à ficha anterior a 2015 e estão vazios. Os encaminhamentos atuais estão em `REDE_SAU`, `ASSIST_SOC`, `ATEND_MULH`, `DELEG_MULH`, `DELEG`, `MPU`, `DEFEN_PUBL`, `INFAN_JUV` e outros.

## 4. Perfil descritivo — mulheres ≥ 18 anos, exceto autoprovocada (n = 30.194)

Percentual de "Sim". Os tipos e vínculos **não são mutuamente exclusivos**, então as linhas não somam 100%.

| Indicador | % |
|---|---:|
| Violência física | 69,0 |
| Violência psicológica/moral | 50,3 |
| Violência sexual | 9,2 |
| Violência financeira/patrimonial | 6,2 |
| Autor: cônjuge | 33,4 |
| Autor: ex-cônjuge | 16,5 |
| Autor: parceiro/ex (cônjuge, ex, namorado, ex) — qualquer | 57,1 |
| Autor do sexo masculino | 78,3 |
| Ocorrência na residência | 75,4 |
| Violência de repetição ("Sim") | 50,5 |
| Motivação registrada como sexismo | 26,8 (37,6% ignorado/não se aplica) |
| Meio: força corporal/espancamento | 62,3 |
| Meio: ameaça | 32,4 |
| Encaminhada à Delegacia da Mulher | 15,6 |
| Encaminhada a outras delegacias | 21,6 |
| Encaminhada à rede de atendimento à mulher | 17,8 |
| Encaminhada ao Ministério Público | 2,8 |
| Encaminhada à Defensoria Pública | 1,4 |

Raça/cor: branca 58,7%, parda 25,4%, preta 6,2%, ignorado 8,0%. Esses números descrevem **notificações**, não a população de vítimas. Sem um denominador populacional, não indicam risco relativo.

Variação 2023→2024 (F, exceto autoprovocada): física 51,5→49,5%, psicológica 38,8→40,9%, sexual 20,9→20,1%. O volume total cresceu 16%. O crescimento pode refletir mais notificação, e não necessariamente mais violência.

## 5. Geografia

- `ID_MN_OCOR` preenchido em praticamente 100%, e 99,5% dos códigos são de municípios do PR.
- Municípios com ao menos uma notificação (F, exceto autoprovocada): 384 em 2023 e 381 em 2024, de **399** no PR.
- Ocorrência = residência em 95,0% dos casos; ocorrência = município notificador em 91,2%.
- Concentração: os 5 maiores municípios somam 29,6% (adultas). Curitiba (`410690`) responde por 11,5%.
- **Células pequenas** (mulheres adultas, município × ano): 212 de 744 têm menos de 5 notificações, e 371 têm menos de 10. Um mapa municipal por ano exigiria supressão ou agregação, por regional de saúde ou comarca.

Diferente do Datajud, aqui existe **município do fato**. Mas ele aparece apenas para quem chegou ao serviço de saúde e foi notificado.

## 6. Implicações para o cruzamento com o Datajud

1. **Ligação individual é impossível e não deve ser tentada.** As bases não têm identificador comum, e o SINAN é desidentificado. O que se pode fazer é um **cruzamento ecológico** por território e período.
2. **Território comum.** O SINAN usa município do fato e o Datajud usa a sede do órgão julgador. A unidade comparável é a **comarca**, que depende da tabela oficial comarca→municípios do TJPR (pendente, CLAUDE.md §5 e §8).
3. **Comparações sustentáveis:** tendência temporal das duas séries, distribuição territorial relativa e, com muita cautela, a razão processos/notificações por comarca, **apresentada como razão entre registros de sistemas distintos, nunca como "taxa de judicialização"**. As unidades, os filtros de entrada e as definições diferem (CLAUDE.md §4).
4. **O SINAN supre variáveis ausentes no Datajud** (vínculo, local, tipo, perfil). Esse perfil vale para a população notificada em saúde e não pode ser transferido para os processos.
5. **Tempo de resposta e medida protetiva:** o SINAN não ajuda. Não registra medida protetiva, e `MPU` é Ministério Público.
6. **Cobertura heterogênea:** a notificação depende da rede de saúde e da prática local. Diferenças entre municípios podem refletir capacidade de notificação.

## 7. Limitações desta exploração

- Apenas dois anos, e só os finais. Não há série histórica nem avaliação de mudanças de ficha.
- Não foi feita deduplicação (`NDUPLIC` vazio). Uma mesma mulher pode ter várias notificações.
- Idade codificada em menos de 1 ano (`NU_IDADE_N < 4000`, 2.465 registros) foi tratada como 0 anos.
- Registros com `LES_AUTOP` ignorado/vazio foram mantidos no recorte "exceto autoprovocada".
- Não houve validação dos códigos de município contra a lista oficial do IBGE (só o prefixo 41).
- Contagens pequenas não foram publicadas aqui. Nada neste relatório está desagregado abaixo do nível estadual, exceto a menção a Curitiba.

## 8. Reprodução

```text
SHA-256 VIOLBR23.dbc 45c042dab40de3fb57a544b606eaa23893d6818e76c0f3ea9006a2c2b664f635
SHA-256 VIOLBR24.dbc 471c7a24b23da053938f449cdc62847e428d21cb72d5d7b6a1c380d6939b2649
```

1. Baixar os arquivos do FTP para `work/sinan/raw/`.
2. Converter: `pyreaddbc.dbc2dbf("VIOLBR23.dbc", "VIOLBR23.dbf")` (idem 24).
3. `python -I docs/artigo/evidencias/scripts/explorar_sinan_pr.py work/sinan/raw` (requer `pandas`, `dbfread`).

O ambiente usado foi um venv temporário fora do projeto. Essas dependências **não** foram adicionadas ao `pyproject.toml`.

## 9. Próximas decisões (para o autor/orientador)

- Incluir o SINAN como fonte contextual ou deixá-lo fora do escopo?
- Recorte etário: ≥ 18 anos? Incluir autoprovocada ignorada?
- Período: alinhar com o recorte do Datajud (o SINAN final vai até 2024).
- Unidade territorial de comparação: comarca ou regional de saúde.
- Avaliar também o SIM (óbitos por agressão, X85–Y09) para feminicídio.
