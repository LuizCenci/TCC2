# Resumo — CNJ, Instituto Avon e Consórcio Lei Maria da Penha (2022)

**Referência:** CONSELHO NACIONAL DE JUSTIÇA; INSTITUTO AVON; CONSÓRCIO LEI MARIA DA PENHA; CEPIA. *Avaliação sobre a aplicação das medidas protetivas de urgência da Lei Maria da Penha*. Brasília: CNJ, 2022. 172 p. ISBN 978-65-5972-074-3. [PDF](https://www.cnj.jus.br/wp-content/uploads/2022/08/relatorio-avaliacao-medidas-protetivas-lei-maria-da-penha-23082022.pdf)

Lido em 01/11/2026 a partir do PDF oficial, com os números conferidos nas tabelas do texto. Os gráficos não puderam ser lidos (são imagens). Resumo de trabalho, não citação literal; antes de citar números no artigo, conferir a página indicada.

## 1. O que é

Relatório final do projeto *Diagnóstico e análise dos metadados do Banco Nacional de Dados do Poder Judiciário (DataJud) sobre Medidas Protetivas de Urgência*. É uma cooperação do CNJ (Departamento de Pesquisas Judiciárias) com o Instituto Avon e o Consórcio Lei Maria da Penha/CEPIA, realizada entre 2021 e 2022. Coordenação: Myllena Calasans de Matos, Leila Linhares Barsted e Wânia Pasinato. Analista de dados: José de Jesus Filho.

**Objetivo principal:** avaliar a **qualidade das informações sobre medidas protetivas (MPUs) cadastradas no Datajud**, e não medir a violência em si.

## 2. Dados e métodos

- **Fonte:** registros do Datajud fornecidos diretamente pelo DPJ/CNJ, **incluindo processos sigilosos**, com nomes, documentos, datas de nascimento e endereços anonimizados. Foram mantidos o sexo e o ano de nascimento de vítimas e agressores. **É um acesso diferente da API pública** usada no TCC, que só traz processos sem sigilo.
- **Recorte principal:** 2.707.750 registros de procedimentos de MPU (2015–2021, com reextração até mai/2022). Filtros: casos novos de **jan/2020 a mai/2022**, **classe 1268** (MPU Lei Maria da Penha – criminal; mais de 60% dos 919.532 registros do período) e **1º grau**. Resultado: **572.159 registros** (p. 33–34).
  - A justificativa para começar em 2020 é a melhor qualidade dos dados após a Resolução CNJ 331/2020. O período "2015–2021" citado em outras fontes é o da extração inicial (etapa 1).
- **Quatro etapas:**
  1. análise descritiva dos metadados;
  2. amostra qualitativa de 2.400 processos públicos de seis tribunais (TJBA, TJDFT, TJES, TJGO, TJPA, **TJPR**);
  3. seis workshops com juízas, servidores, MP, Defensoria, delegadas e patrulhas;
  4. estudo de caso no TJDFT, com questionário e entrevistas.
- **Tempo até a decisão:** análise de sobrevivência (**Kaplan-Meier**, teste log-rank), em **horas**. O início é o primeiro movimento "Recebimento" ou "Distribuição"; o evento é a decisão sobre a MPU; os pedidos ainda não decididos são tratados como **censurados** (p. 58–60).

## 3. Estrutura e principais achados

| Capítulo (autoria) | Achados |
|---|---|
| **Introdução** | Revisão no Portal CAPES: 28–29 artigos sobre MPUs, quase todos **qualitativos e locais**. Faltam estudos quantitativos de abrangência ampla. Debate sobre a **natureza jurídica** das MPUs: cautelar penal, vinculada a processo criminal (corrente majoritária), × tutela autônoma/cível |
| **1. Análise descritiva dos metadados** (Pasinato; Severi) | Distribuição desigual entre tribunais, explicada por remessa incompleta e uso incorreto das TPUs, não por diferenças reais de judicialização. **Sigilo:** 29,2% nível 0 (público), 38,7% nível 1, 20,5% nível 2, 9,7% nível 3, 2,0% nível 4. 145 varas exclusivas no país em 2021, com 45% das MPUs. **Tipo de medida** preenchido em só **30,5%** dos registros: aproximação e contato, art. 22, III, a/b, são 77%; afastamento do lar, 19,6%. Não é possível avaliar o efeito da pandemia com o Datajud |
| **2. Tempo para a medida protetiva** (Jesus Filho; Severi) | A maioria dos tribunais **não decide todos os pedidos em 48 h**; em média, **30%** seguem pendentes após 48 h. TJDFT é o mais rápido (22% decididos na 1ª hora); TJMG e TJRJ os mais lentos. Diferenças entre tribunais significativas (log-rank). **Decisões de indeferimento demoram mais.** O efeito do tipo de vara (exclusiva × não exclusiva) varia por tribunal |
| **3. Análise de amostra de processos** (Campos; Castilho; Villarroel; José) | A maior parte das informações exigidas pelo Datajud **existe nos autos**; o problema é a transcrição para o sistema (parametrização das TPUs, capacitação). Raça/cor, escolaridade e ocupação nem sempre estão nos processos. Acesso aos autos foi difícil em todos os tribunais |
| **4. Efetividade do BNMPU no TJDFT** (Castilho et al.) | Entrevistas e questionário com 40 juizados e varas: dificuldades de alimentação dos sistemas, críticas e conhecimento do painel |
| **5. Segredo de justiça e sigilo** (Matos; Barsted; José) | **Não há critério uniforme** para decretar sigilo; o principal fundamento é o **Enunciado 34 do FONAVID**, que orienta processar MPUs em segredo de justiça. O sigilo alto protege a privacidade, mas **inviabiliza pesquisa e monitoramento** e dificulta o acompanhamento da medida pela rede de atendimento |
| **6. Workshops** (Matos; Severi) | Sobrecarga para alimentar os sistemas; entendimentos diferentes sobre a natureza jurídica e os fluxos; MPUs registradas por vários tipos de movimento (liminar, antecipação de tutela, decisão interlocutória, sentença); sigilo como obstáculo |
| **Conclusões e recomendações** | O Datajud tem **potencial** para os indicadores de monitoramento da Lei Maria da Penha, mas os dados ainda são **insuficientes**. Recomenda ao CNJ: (1) estudar obstáculos à adoção das TPUs e produzir guias de preenchimento; (2) GT para **parâmetros de sigilo**; (3) jornada sobre natureza jurídica, **duração da vigência** das MPUs e competência das varas exclusivas; (4) GT sobre o Formulário Nacional de Avaliação de Risco |
| **Anexo** | Guia para servidores, com os códigos de movimento: **11423 Concessão, 11424 Concessão em parte**, 11425 Não-concessão, 11426 Revogação |

## 4. Números do TJPR no relatório (jan/2020–mai/2022)

| Indicador | TJPR | Fonte no relatório |
|---|---:|---|
| Registros de MPU (classe 1268, 1º grau) | **89.404–89.405** (2º maior do país, 15,6%) | Cap. 2, Tab. 1; Cap. 5, Tab. 2 |
| Processos de violência doméstica (VDFM) | 132.172 | Cap. 2, Tab. 1 |
| MPUs por 100 mil mulheres | 1.522 (3º maior) | Cap. 2, Tab. 1 |
| Deferidas / indeferidas | 94,96% / 5,04% | Cap. 2, Tab. 2 |
| Pedidos em varas exclusivas | 45,21% | Cap. 2, Tab. 3 |
| Pendentes após 1 h / 12 h / 24 h / **48 h** / 120 h | 89% / 46% / 30% / **17%** / 9,9% | Cap. 2, Tab. 4 |
| Diferença de tempo entre vara exclusiva e não exclusiva | curvas "caminham juntas" | Cap. 2 |
| **Sigilo nível 0 (público)** | **4.420 (4,9%)** | Cap. 5, Tab. 2 |
| **Sigilo nível 2** | **74.035 (≈83%)** | Cap. 5, Tab. 2 |

Referências locais citadas pelo relatório, a incluir na revisão (`11`): CEVID-TJPR/UFPR, *Medidas protetivas de urgência: perspectivas desde o pedido à sua decisão* (Curitiba, 2022); SÁ, P. P. (coord.), *Dossiê Feminicídio: por que aconteceu com ela?* (Curitiba: TJPR, 2021).

## 5. Implicações para o TCC

1. **Cobertura (achado crítico).** No TJPR, só cerca de **5% dos registros de MPU são públicos**; cerca de 83% estão em sigilo nível 2. A API pública trouxe cerca de 2.350 registros da classe 1268 por ano em 2020–2022 (`08` §7), na mesma ordem de grandeza dos 4.420 públicos em 29 meses do relatório (cerca de 1.800 por ano). **A base do TCC representa a fatia pública, provavelmente pequena e possivelmente não aleatória, das medidas protetivas do PR.** Nenhuma contagem de MPU do TCC pode ser lida como volume real. Isso também deve valer, em grau a medir, para os demais processos de violência doméstica: o relatório conta 132.172 processos de VDFM no TJPR em 29 meses, cerca de 55 mil por ano, contra 14–25 mil por ano na base do TCC. Esta é a resposta concreta à pergunta 6 do roteiro jurídico (`09`). **Declarar como principal limitação.**
2. **Método de tempo convergente.** O relatório usa Kaplan-Meier com censura, como o `08` §4. O TJPR decide **83% dos pedidos em até 48 h**, coerente com a mediana de 0 dias encontrada pelo TCC. Diferenças: o relatório mede em horas e parte do movimento de recebimento ou distribuição; o TCC mede em dias a partir de `dataAjuizamento`. Comparar com cautela, porque as populações são diferentes (todas as MPUs × só as públicas).
3. **Códigos validados.** O guia do relatório confirma o uso dos movimentos 11423–11426 adotado no `07` §5. O relatório também relata MPUs registradas por **outros movimentos** (liminar, antecipação de tutela, decisão interlocutória, sentença), o que explica parte dos registros 1268 sem movimento 11423–11425.
4. **Tipo de medida e complementos.** O relatório encontrou o tipo de medida em só 30,5% dos registros nacionais. Vale medir esse preenchimento na base do TCC (complementos dos movimentos de MPU).
5. **Natureza jurídica.** O debate entre MPU cautelar penal e autônoma explica por que a MPU é um processo separado (classe 1268), às vezes apensado ao criminal (`07` §3). A unidade de contagem por procedimento é coerente com isso.
6. **Posicionamento.** O relatório confirma a lacuna: há poucos estudos quantitativos e abrangentes, e o acesso a dados é a principal barreira. O TCC é complementar: **o que é possível medir só com o dado público**, de forma reprodutível, e quanto esse dado deixa de fora.

## 6. Pendências

- Medir na base do TCC a distribuição de `nivelSigilo`. Já se sabe que é 100% nível 0 (`06`), mas falta confirmar se há registros com sigilo apenas de documentos.
- Buscar o relatório CEVID-TJPR/UFPR (2022) e o Dossiê Feminicídio (TJPR, 2021).
- Atualizar a CLAUDE.md §4.2 e §15 com a estimativa de cobertura, se o autor concordar.
