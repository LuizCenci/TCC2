# Análise de parâmetros para a coleta Bronze — TJPR

Data das consultas: 17/10/2026. Endpoint: `api_publica_tjpr/_search`.
Método: 9 consultas de **agregação** (`size: 0`, `track_total_hits: true`). Elas retornam apenas contagens; nenhum processo foi baixado. Consultas, respostas e scripts estão em `evidencias/datajud_agregacoes_20261017/` e `evidencias/scripts/`.

Status: **achados verificados**. As recomendações da §7 foram **decididas pelo autor em 18/10/2026** e estão consolidadas, com os parâmetros finais, em `01-parametros-da-extracao.md`. Após esta análise, a busca no SGT/CNJ acrescentou códigos de completude (15309, 12423, 12358, 15511) e o 9647, equivalente infracional do 5560; ver o documento 01, §4.

Siglas: PVD = catálogo de 15 assuntos do glossário "Justiça pela Paz em Casa" (`config/catalogs/pvd_cnj_2025-07-17.yaml`). MPU = medida protetiva de urgência (classe 1268). JVDFM = Juizado de Violência Doméstica e Familiar contra a Mulher.

## 1. Extrair tudo ou só violência?

**Só violência, com filtro temático amplo.** O TJPR tem **8,9 milhões** de registros ajuizados entre 2019 e 2026 fora do catálogo PVD, somando todos os graus. Baixar tudo seria inviável, desrespeitaria a infraestrutura do CNJ (CLAUDE.md §8) e encheria a Bronze de dados sem utilidade. O universo temático em G1 fica perto de **150 mil registros** (§5), o que é perfeitamente coletável.

A estratégia é **ampliar na Bronze e restringir na Silver**. A Bronze traz o núcleo e também as extensões candidatas, cada uma identificada pela consulta que a trouxe. A Silver decide o que entra em cada indicador e registra o motivo.

## 2. Período

Registros PVD por ano de ajuizamento, todos os graus:

| Ano | <2015 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026* |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Total | 6.804 | 4.442 | 6.525 | 9.957 | 18.603 | 20.704 | 20.173 | 17.685 | 18.332 | 20.143 | 22.175 | 22.290 | 11.726 |
| G1 | 6.793 | 4.435 | 6.509 | 9.907 | 18.364 | 19.146 | 17.595 | 13.871 | 13.690 | 15.145 | 16.687 | 18.357 | 10.153 |

\* 2026 está incompleto (consulta em outubro).

- **Começar em 2019 é defensável.** Entre 2015 e 2018 o volume cresce 4×, o que provavelmente reflete a adoção dos códigos PVD, e não necessariamente mais processos (hipótese). Antes de 2019 a série tende a ser incomparável.
- **Coletar 2026, mas analisar só anos completos.** Na análise, 2026 entra só como monitoramento ou fica de fora; o recorte analítico recomendado é **2019–2025**.
- **Há uma queda em 2021–2022, mesmo somando as extensões.** O total G1 com extensões vai de cerca de 25 mil em 2019–2020 para cerca de 15 mil em 2021. Causas possíveis, todas a investigar: pandemia, mudança de codificação, migração de sistema. Isso deve ser tratado como achado a explicar, não como tendência real.

## 3. Grau

| Grau | PVD (todos os anos) | Observação |
|---|---:|---|
| G1 | 170.652 | Núcleo. Processos originários. |
| G2 | 28.081 | Recursos (apelação, HC). É **o mesmo caso em outra instância**; incluir duplicaria processos. |
| JE | 822 | Juizado Especial; a Lei Maria da Penha (art. 41) afasta a Lei 9.099. Provável classificação atípica. |
| TR | 4 | Desprezível. |

**Recomendação:** coletar só G1. JE é opcional e barato (cerca de 100 por ano), útil só como diagnóstico. G2 fica fora, salvo se surgir uma pergunta sobre recursos.

## 4. Assuntos e classes — o que o catálogo PVD deixa de fora

### 4.1 Núcleo PVD (confirmado empiricamente)

Os mais usados em G1 2019–2026: 10949 *Violência Doméstica contra a Mulher* (penal), 12194 *Contra a Mulher* (lesão corporal), 14227 *Descumprimento de MPU*, 14943 *Lesão em razão da condição de mulher*, 11979 (infracional), 12196, 14942 *Violência psicológica*.

Códigos PVD **pouco ou nada usados** no TJPR: 10948 (cível, 88), 14226 (49), 14097 e 14098 (fora do top 150). Eles não atrapalham e devem continuar no filtro.

**Mudança de codificação em 2021:** o código 14943 (lesão em razão da condição de mulher, Lei 14.188/2021) sobe de 51 em 2019 para 4.121 em 2025, enquanto 12194 cai. Na Silver, categorias por assunto precisam considerar esse período.

### 4.2 Extensões candidatas (G1, 2019–2026, **sem nenhum código PVD**)

| Extensão | Fora do PVD | Já com PVD | Natureza | Recomendação |
|---|---:|---:|---|---|
| **Classe 1268** — MPU (Lei Maria da Penha) | 3.239 | 15.631 | Específica de violência contra a mulher | **Incluir.** Sem ela, cerca de 17% das MPUs se perdem. |
| **Assunto 12091** — Feminicídio | 2.736 | 823 | Específica por definição | **Incluir.** 77% dos feminicídios não têm código PVD. |
| **Assunto 5560** — Lesão corporal *decorrente de violência doméstica* | 12.127 | 1.867 | VD **genérica** (vítima de qualquer sexo) | **Coletar e marcar como ambígua.** Ver nota abaixo. |
| **Assuntos 14684/14686** — Perseguição | 998 | 940 | Não específica; agravada quando contra mulher | Coletar como secundária; decidir na Silver. |
| Classe 12423 | 0 | — | — | Retirar do diagnóstico (sem registros). |

**Nota sobre o 5560.** Esse código tem **5.203 registros em 2019 e 6.360 em 2020**, contra 555 em 2021 e praticamente zero a partir de 2022. Ele foi substituído pelos códigos específicos (12194/14943). Usar só o PVD deixa de fora um volume equivalente a **27% (2019) e 36% (2020)** da contagem PVD desses anos e cria uma quebra artificial na série. Mas o 5560 inclui vítimas homens, crianças e idosos, então não pode entrar como "violência contra a mulher" sem qualificação. Proposta para a Silver: duas séries, uma estrita (PVD + 1268 + 12091) e uma ampliada (+ 5560), apresentadas como **análise de sensibilidade** (CLAUDE.md §12).

### 4.3 Marcador de exclusão

O assunto **12195** — *Contra pessoas não identificadas como mulher* — aparece em 139 registros que **têm** código PVD e em cerca de 920 fora dele, com uso crescente. Deve ser coletado e virar uma flag de exclusão ou revisão na Silver, sem filtrar na Bronze.

### 4.4 O que não incluir no filtro

- **3402 Ameaça** (cerca de 109 mil fora do PVD), **12345 Vias de fato**, **3386 Lesão leve**, **3465/11417 Estupro**: são genéricos. Incluí-los traria majoritariamente casos sem relação com o tema (CLAUDE.md §10). Esses assuntos **já aparecem** como assuntos secundários nos processos PVD e chegam à Bronze por esse caminho.
- **Filtro por órgão (JVDFM).** Só 7 cidades têm juizado especializado. Esses juizados acumulam crimes contra crianças e idosos, e 13.520 processos G1 neles não têm código PVD; os mais comuns são Ameaça, 5560, Estatuto do Idoso e ECA. Filtrar por órgão traria ruído e deixaria de fora o interior. Ainda assim, vale **uma partição diagnóstica** opcional para medir o que escapa.

## 5. Volume estimado da coleta (G1, 2019–2026)

| Partição | Registros |
|---|---:|
| Núcleo PVD | 124.644 |
| Extensões (1268, 12091, 5560, perseguição) sem PVD | 18.616 |
| **Total recomendado** | **≈ 143 mil** |
| Diagnóstico opcional: JVDFM sem PVD (sobrepõe-se parcialmente às extensões) | até 13.520 |

Com 100 registros por página, são cerca de 1.430 requisições. Isso é viável com as pausas e os retries já implementados. A média é de 1,9 assunto por processo, com máximo de 12.

## 6. Outros parâmetros e campos observados

- **`nivelSigilo` = 0 em 100% dos registros.** O índice público **não contém processos sigilosos**. Como parte dos casos de violência doméstica tramita em segredo de justiça, essa é uma limitação de cobertura importante (CLAUDE.md §4.2) e precisa constar no artigo.
- **`orgaoJulgador.codigoMunicipioIBGE`** está sempre preenchido, com 163 municípios distintos, que correspondem às sedes de comarca e não aos 399 municípios do estado. Isso confirma que o mapa será **por sede judicial** (CLAUDE.md §4.4–4.5).
- **`sistema`**: 99% Eproc mesmo em 2019. O campo reflete o sistema **atual**, provavelmente após migração, e não serve para estratificação histórica.
- **`formato`**: 100% eletrônico, sem variação útil.
- **`_source` completo.** Não restringir campos na Bronze. Movimentos e complementos, necessários para identificar concessão de MPU na Silver, vêm junto. O catálogo de **movimentos** (concessão, indeferimento, revogação de MPU) é decisão da Silver.

## 7. Decisões (tomadas pelo autor em 18/10/2026)

1. **Período:** coleta 2019–2026; análise **2019–2025**. 2026 fica fora da análise por opção do autor (ano incompleto).
2. **Grau:** só G1.
3. **Filtro:** núcleo PVD **ou** extensões específicas (classe 1268, feminicídio etc.), ambíguas (5560, 9647) e secundárias (perseguição). O grupo que justificou cada inclusão é derivado na Silver.
4. **Partição diagnóstica por órgão (JVDFM):** não incluída.
5. **Classe 12423:** passou da consulta diagnóstica para o filtro principal, como extensão de completude; a consulta diagnóstica foi desativada.
6. **Catálogo:** nova versão `config/catalogs/tjpr_vcm_2026-10-18.yaml`; a PVD original permanece intacta.
