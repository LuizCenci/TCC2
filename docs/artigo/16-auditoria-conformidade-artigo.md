# Auditoria de conformidade: artigo × CLAUDE.md × documentação × implementação

Data: 05/11/2026. Fonte oficial do TCC: `Template_Artigo_COENS (3).pdf` (6 p., lido integralmente nesta data). Comparado com: CLAUDE.md v5, `docs/artigo/01–15`, `readme.md` e o código na `master` (`6f555f1`; 69 testes passando, 2 ignorados).

Legenda:
- ✅ **conforme**;
- ⚠️ **divergente**: o artigo promete algo que os dados ou a implementação não sustentam como está escrito; recomenda-se ajustar o texto (decisão do autor);
- 🕒 **pendente**: previsto e ainda não feito;
- 🔧 **corrigido nesta auditoria**: erro interno nos documentos.

## 1. Objetivos e escopo

| Artigo (seção) | Situação | Evidência / observação | Recomendação |
|---|---|---|---|
| Objetivo geral: *dataset* consolidado e ferramenta de visualização de indicadores (§1.1) | 🕒 | Bronze completa (147.002 registros, `06`, `13`); Silver, Gold e dashboard pendentes | — |
| Obj. 1: pipeline de extração respeitando as restrições do CNJ | ✅ | Coleta sequencial, retomada, tratamento de 429/504, sem rotação de identidade (`03`, `06`, `13`) | Citar os números de `03` e `06` no artigo |
| Obj. 2: limpeza, anonimização (LGPD) e enriquecimento IBGE | 🕒 ⚠️ | Desenho da Silver em `10`. A API **não traz nomes das partes**; o identificador sensível é o número do processo | Trocar "anonimização" por "**minimização e pseudonimização**": hash não é anonimização (CLAUDE.md §13) |
| Obj. 3: dashboard interativo | 🕒 | Não iniciado | — |
| Obj. 4: subsídios para políticas públicas | ⚠️ | Os dados medem a **judicialização do acervo público**, não a violência (CLAUDE.md §4) | Ver §2 |
| Período de análise | ⚠️ | **O artigo não informa o período.** Decisão vigente: **2019–2026**, com 2026 parcial (`01` §2, `13`) | Incluir período, grau (G1), catálogo e data dos retratos do índice na Metodologia |
| Recorte temático: "filtragem baseada na TPU para isolar **estritamente** os casos", na Silver (§4) | ⚠️ | A filtragem pela TPU já ocorre **na extração (Bronze)**, por catálogo versionado (`01` §4). Na Silver haverá séries **estrita** e **ampliada** (`07` §8) | Descrever que o filtro temático é aplicado na consulta à API e refinado na Silver; "estritamente" vale só para a série estrita |

## 2. Afirmações do artigo que os dados não sustentam como estão escritas

| Trecho (seção) | Por que diverge | Achado |
|---|---|---|
| "mapear a **dinâmica dos crimes de gênero**", "**dinâmicas de agressão**", "**características das agressões**" (Resumo, §1, §3, §6) | A fonte não tem dados do fato nem da vítima; mede processos | CLAUDE.md §4.1–4.3, §7; inventário de campos em `docs/exemplos/` |
| "indicadores espaciais e **evidências científicas precisas**", "**investigue causas**", "**mitigação** dos crimes" (Resumo, §1, §4, §7) | Análise descritiva não demonstra causa nem efeito | CLAUDE.md §4.9 |
| "a própria **eficiência da resposta do judiciário**" (§1) | Diferenças entre unidades refletem composição, cobertura e prática de registro | CLAUDE.md §4.10; `08` §7; `14` §6 |
| "**tempo médio** de resposta para a concessão de medidas de urgência **por comarca**" (§1) | **Viável**, mas: (a) só ≈**5%** das MPUs do TJPR são públicas (`12`); (b) usar mediana e sobrevivência, não média; (c) N por comarca muito pequeno | `07` §5 (mediana de 0 dias); `08` §6; `12` §4–5 |
| "superar a **dependência de registros policiais**" (Resumo) | A fonte judicial tem seus próprios filtros (sigilo, acesso à Justiça) e não elimina a subnotificação | CLAUDE.md §4.3; `12` |
| "**inferir a geografia das comarcas** a partir dos órgãos julgadores" (§1) | ✅ viável, com ressalva: é a **sede do órgão atual**, não o local do fato; falta a tabela oficial comarca → municípios | `08` §6; `09` §4.A |
| "**georreferenciamento dos registros**" (§4) | É georreferenciamento da **sede judicial** (163 municípios), não dos fatos | CLAUDE.md §4.4–4.5 |

## 3. Arquitetura e tecnologias

| Artigo | Situação | Observação |
|---|---|---|
| Medalhão: Bronze → Silver → Gold → dashboard (§3.1, §4) | ✅ | Implementação e desenho seguem as camadas (`06`, `10`) |
| Python | ✅ | — |
| **Prefect**: "coordenação e agendamento do fluxo, garantindo o **tratamento de falhas temporárias** na comunicação com a API" (§3.2) | ✅ com ressalva | Implementado para a **base operacional** (`15`). As falhas de comunicação são tratadas **pelo cliente**; o Prefect agenda e faz uma nova tentativa por partição. A **coleta da base do artigo foi manual**. Descrever essa divisão no artigo |
| **PostgreSQL com PostGIS** (§3.2) | 🕒 | Próximo passo. **PostGIS:** mapas por código municipal não exigem PostGIS (CLAUDE.md §9); para cumprir o artigo, instalar a extensão e carregar as geometrias do IBGE na Gold |
| Anonimização na Silver: "**descarte** de quaisquer informações que identifiquem as partes" (§4) | ⚠️ | O modelo (`10`) **isola** o número do processo em esquema restrito, porque ele é necessário para deduplicar e rastrear. Decidir: descarte após a deduplicação **ou** isolamento justificado. Os dois são defensáveis, mas o artigo deve descrever o que de fato será feito |
| Gold: órgãos julgadores cruzados com o IBGE (§4) | ✅ viável | `codigoMunicipioIBGE` 100% preenchido, 7 dígitos (`docs/exemplos/campos_api.json`) |

## 4. Cronograma (§5)

| Etapa no artigo | Meses previstos | Situação em 05/11/2026 |
|---|---|---|
| Estudo da API | jun–jul | ✅ (piloto em 03/10; achados em `docs/anotações tcc.md`) |
| Bronze | jul–ago | ✅ concluída em 18/10 e 05/11 |
| Silver | ago–set | 🕒 não iniciada |
| Gold | set–out | 🕒 não iniciada |
| Dashboard | out–nov | 🕒 não iniciado |
| Análise investigativa | out–dez | parcial (viabilidade: `07`, `08`, `14`) |

O cronograma do artigo previa a Silver e a Gold concluídas até outubro; em novembro ambas estão pendentes. O prazo de entrega real não está registrado (CLAUDE.md §14). **Recomenda-se revisar o cronograma com o orientador** e priorizar o caminho mínimo: Silver → indicadores → dashboard simples.

## 5. Resultados esperados e limitações (§6, §6.1)

| Artigo | Situação |
|---|---|
| Banco "ágil e resiliente", que "indexa e **atualiza** o acervo" | ✅ a atualização é viável pela coleta incremental com marca d'água (`15`); banco 🕒 |
| Diagnóstico espacial e jurimétrico | ⚠️ ver §2: padrões da **geografia judicial** do acervo público |
| Limitação: subnotificação e erros de classificação | ✅ confirmada: mudança de códigos em 2021, códigos infracionais em ações penais, marcadores contraditórios (`07`, `08`) |
| Limitação: dados faltantes e georreferenciamento | ✅ prevista; na prática a geografia está 100% preenchida, mas é da sede |
| Limitação: instabilidade da fonte | ✅ confirmada: latência de cerca de 25 s, corte de 60 s, 429 por hora (`03`) |
| **Limitações ausentes no artigo** (a acrescentar) | ⚠️ (1) **sigilo**: só ≈5% das MPUs do TJPR são públicas (`12`); (2) **atraso de indexação** de 1–2 meses e índice não estático (`13`); (3) unidade = procedimento ≠ caso ≠ vítima, sem ligação entre processos do mesmo fato (`07` §3); (4) órgão e classe **atuais**; (5) anomalias 2019–2020 e mudança de prática processual (`08` §7); (6) 2026 parcial |

## 6. Referências do artigo (§8)

| Item | Situação |
|---|---|
| **Moroskoski et al. (2025)** | ✅ **existe**: *Feminicídio: análise espacial e fatores associados aos crimes de gênero no Paraná, Brasil*. *Ciência & Saúde Coletiva*, v. 30, n. 10, e10862025, 2025. DOI 10.1590/1413-812320253010.10862025. Usa denúncias de feminicídio do MP-PR (2015–2022; 1.672). 🔧 **A afirmação anterior de que não foi localizado estava errada e foi corrigida** no CLAUDE.md §16 e em `11`. O dado "82% sem MPU" refere-se a **vítimas de feminicídio** dessa base; não generalizar |
| Bogo et al. (2025) e Klen et al. (2020) | ⚠️ "[Nome da Instituição]" ainda como placeholder |
| Mariano Junior (2021) | ⚠️ nas referências, mas **não citado no texto** |
| "de Salles (2025)" no texto × "SALLES" nas referências | Conferir a forma de citação (ABNT/SBC) |
| Nota "técnico.1" (§4) | ⚠️ marca de nota sem texto de nota |
| Literatura levantada em `11`–`12` (CNJ 2022, Pinto et al. 2026, Leal et al. 2021/UTFPR, Leandro et al. 2024, CEVID-TJPR 2022) | Sugestão: incorporar, sobretudo CNJ (2022), que usa a mesma fonte e o mesmo tema |
| Revisão textual | "Para, definem-se" (§1.1); "seuintes" (§6.1); "metadados de judiciais" (§3) |

## 7. Consistência interna (CLAUDE.md, documentação e código)

| Item | Situação |
|---|---|
| Hashes do catálogo e das configurações × `01` §10 e `13` | ✅ conferem (`df83d3ab…`, `e33374d7…`, `c73f578b…`) |
| Testes na `master` | ✅ 69 passando; 2 ignorados (ao vivo; orquestrador sem o extra `orquestracao`, que passa na branch `orquestrador` com o Prefect: 75) |
| CLAUDE.md §7: órgão do movimento como `codigoOrgao`/`nomeOrgao` | 🔧 corrigido para `codigo`/`nome`, o que a API realmente retorna (`docs/anotações tcc.md`) |
| `10` (modelo Silver): `em_analise` = "2019–2025" | 🔧 corrigido para 2019–2026, com a regra de seleção das partições (`13` §6) |
| `config/collection.bronze.yaml`, linha 3: comentário "2026 … excluído da análise" | ⚠️ desatualizado, mas **mantido** de propósito: alterar o arquivo mudaria o SHA-256 documentado da coleta definitiva. A decisão vigente está em `01` §2 |
| `07`, `08`, `14`: números calculados sobre 2019–2025 | Registros históricos da análise de viabilidade. Recalcular os indicadores finais com 2019–2026 na Silver |
| CLAUDE.md §9: "primeiro um fluxo pequeno de ponta a ponta; depois Prefect" | ⚠️ o orquestrador veio antes da Silver, por decisão do autor; está documentado (`15` §7) |
| Branches | `master` contém tudo; `datajud-bronze-pilot` e `orquestrador` estão atrás ou integradas; nada enviado ao GitHub |

## 8. Decisões do autor após a auditoria (05/11/2026)

- **Número do processo:** manter **isolado** em esquema restrito, como no modelo (`10`), por enquanto. O texto do artigo sobre "descarte" fica a ajustar.
- **PostGIS:** será usado **na Gold** (geometrias do IBGE e mapa), como prevê o artigo (§3.2).
- **Forma de trabalho:** implementação por plano SDD executado por subagente Sonnet, sempre na `master` (CLAUDE.md §18, item 8).

## 9. Prioridades sugeridas

1. **Revisar o texto do artigo** (§2 e §5): reformular de "violência" para **"judicialização no acervo público"**; acrescentar período, recorte e as limitações novas, sobretudo o sigilo. A formulação de título e pergunta proposta no CLAUDE.md §3 já vai nessa direção.
2. **Decidir o tratamento do número do processo** (descarte × isolamento) antes de implementar a Silver.
3. **Decidir se o PostGIS entra** (o artigo promete); a recomendação é instalar e usar na Gold para o mapa.
4. **Revisar o cronograma** com o orientador.
5. Corrigir as referências (placeholders, Mariano Junior, nota de rodapé).
