--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3
-- Dumped by pg_dump version 16.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: controle; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA controle;


--
-- Name: gold; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA gold;


--
-- Name: ref; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA ref;


--
-- Name: restrito; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA restrito;


--
-- Name: silver; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA silver;


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: execucao_coleta; Type: TABLE; Schema: controle; Owner: -
--

CREATE TABLE controle.execucao_coleta (
    run_id text NOT NULL,
    catalogo_versao text,
    catalogo_sha256 character(64),
    config_hash character(64),
    versao_coletor text,
    updated_since text,
    status_coleta text,
    criada_em timestamp with time zone,
    concluida_em timestamp with time zone,
    carregada_em timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: execucao_gold; Type: TABLE; Schema: controle; Owner: -
--

CREATE TABLE controle.execucao_gold (
    versao_regras text NOT NULL,
    construida_em timestamp with time zone DEFAULT now() NOT NULL,
    contagens jsonb
);


--
-- Name: pagina_bronze; Type: TABLE; Schema: controle; Owner: -
--

CREATE TABLE controle.pagina_bronze (
    run_id text NOT NULL,
    ano smallint NOT NULL,
    pagina integer NOT NULL,
    sha256 character(64) NOT NULL,
    n_registros integer NOT NULL,
    total_api integer
);


--
-- Name: agg_categoria; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_categoria (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    ano_parcial boolean,
    tipo_procedimento text,
    mesorregiao_id integer,
    categoria text,
    serie text NOT NULL,
    n bigint NOT NULL
);


--
-- Name: agg_cautelar; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_cautelar (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    ano_parcial boolean,
    tipo_procedimento text,
    categoria text,
    serie text NOT NULL,
    n bigint NOT NULL,
    n_flagrante bigint,
    n_preventiva bigint,
    n_liberdade_provisoria_concedida bigint
);


--
-- Name: agg_cobertura_cnj; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_cobertura_cnj (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    ano_parcial boolean,
    medida text,
    n_base bigint,
    n_cnj bigint,
    pct numeric,
    n bigint NOT NULL
);


--
-- Name: agg_desfecho; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_desfecho (
    pergunta text DEFAULT 'Q10'::text NOT NULL,
    tipo_procedimento text NOT NULL,
    serie text NOT NULL,
    variante text NOT NULL,
    estrato text NOT NULL,
    valor_estrato text NOT NULL,
    desfecho text NOT NULL,
    n bigint NOT NULL,
    n_desfecho bigint NOT NULL,
    estimavel boolean NOT NULL,
    ia_365 double precision,
    ia_730 double precision,
    ia_1095 double precision,
    ia_1825 double precision
);


--
-- Name: agg_mpu; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_mpu (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    ano_parcial boolean,
    mesorregiao_id integer,
    orgao_especializado boolean,
    serie text NOT NULL,
    n bigint NOT NULL,
    n_com_decisao bigint,
    n_deferimento bigint,
    n_parcial bigint,
    n_indeferimento bigint,
    n_revogadas bigint
);


--
-- Name: agg_mpu_medida; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_mpu_medida (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    ano_parcial boolean,
    mesorregiao_id integer,
    tipo_medida text,
    n bigint NOT NULL
);


--
-- Name: agg_pipeline; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_pipeline (
    pergunta text NOT NULL,
    run_id text,
    concluida_em timestamp with time zone,
    updated_since text,
    carregada_em timestamp with time zone,
    versao_regras text,
    construida_em timestamp with time zone,
    n bigint NOT NULL
);


--
-- Name: agg_qualidade_orgao; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_qualidade_orgao (
    pergunta text NOT NULL,
    orgao_codigo integer,
    mesorregiao_id integer,
    orgao_especializado boolean,
    n bigint NOT NULL,
    media_movimentos numeric(12,2),
    mediana_movimentos double precision,
    n_processos_com_duplicado bigint
);


--
-- Name: agg_taxa; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_taxa (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    ano_parcial boolean,
    tipo_procedimento text,
    serie text NOT NULL,
    mesorregiao_id integer,
    n bigint NOT NULL,
    pop_feminina bigint,
    taxa_bruta_100k double precision,
    taxa_eb_100k double precision
);


--
-- Name: agg_tempo; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_tempo (
    pergunta text NOT NULL,
    marco text NOT NULL,
    tipo_procedimento text,
    serie text NOT NULL,
    estrato text NOT NULL,
    valor_estrato text NOT NULL,
    n bigint NOT NULL,
    n_eventos bigint NOT NULL,
    estimavel boolean NOT NULL,
    mediana_dias double precision,
    mediana_alcancada boolean,
    ic95_inf double precision,
    ic95_sup double precision,
    pct_evento_ate_2 double precision,
    pct_evento_ate_30 double precision,
    pct_evento_ate_365 double precision,
    pct_evento_ate_730 double precision
);


--
-- Name: agg_volume; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_volume (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    ano_parcial boolean,
    mes_ajuizamento integer,
    tipo_procedimento text,
    mesorregiao_id integer,
    serie text NOT NULL,
    n bigint NOT NULL
);


--
-- Name: agg_volume_jan_ago; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.agg_volume_jan_ago (
    pergunta text NOT NULL,
    ano_ajuizamento integer,
    tipo_procedimento text,
    mesorregiao_id integer,
    serie text NOT NULL,
    n bigint NOT NULL
);


--
-- Name: fato_evento; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.fato_evento (
    registro_id bigint NOT NULL,
    seq integer NOT NULL,
    dt_evento timestamp with time zone,
    dias_desde_ajuizamento integer,
    movimento_codigo integer,
    fase text NOT NULL,
    subtipo text,
    orgao_codigo integer
);


--
-- Name: fato_processo; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.fato_processo (
    registro_id bigint NOT NULL,
    run_id text NOT NULL,
    data_corte date,
    ano_particao integer,
    classe_codigo integer,
    tipo_procedimento text,
    juri boolean,
    orgao_codigo integer,
    orgao_especializado boolean,
    municipio_sede_ibge integer,
    mesorregiao_id integer,
    data_ajuizamento timestamp without time zone,
    ano_ajuizamento integer,
    mes_ajuizamento integer,
    serie_estrita boolean,
    feminicidio_tentado boolean,
    infracional boolean,
    n_movimentos integer,
    numero_repetido boolean,
    removido_indice boolean,
    data_ajuizamento_nula boolean,
    dt_distribuicao date,
    dt_decisao_mpu date,
    dt_revogacao_mpu date,
    dt_recebimento_denuncia date,
    dt_primeira_audiencia date,
    dt_sentenca date,
    dt_transito date,
    dt_arquivamento date,
    resultado_mpu text,
    desfecho text,
    desfecho_subtipo text,
    dt_desfecho date,
    duracao_dias integer,
    censurado boolean,
    reativado boolean,
    evento_antes_ajuizamento boolean
);


--
-- Name: processo_categoria; Type: TABLE; Schema: gold; Owner: -
--

CREATE TABLE gold.processo_categoria (
    registro_id bigint NOT NULL,
    categoria text NOT NULL,
    somente_ampliada boolean NOT NULL
);


--
-- Name: movimento_fase; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.movimento_fase (
    movimento_codigo integer NOT NULL,
    movimento_nome text,
    fase text NOT NULL,
    subtipo text
);


--
-- Name: movimento; Type: TABLE; Schema: silver; Owner: -
--

CREATE TABLE silver.movimento (
    movimento_id bigint NOT NULL,
    registro_id bigint NOT NULL,
    codigo integer,
    nome_original text,
    data_hora timestamp with time zone,
    dias_desde_ajuizamento integer,
    orgao_codigo_original text,
    orgao_codigo integer,
    orgao_nome text,
    ordem_original integer NOT NULL,
    ordem_cronologica integer NOT NULL
);


--
-- Name: qualidade_cobertura_referencias; Type: VIEW; Schema: gold; Owner: -
--

CREATE VIEW gold.qualidade_cobertura_referencias AS
 WITH cod AS (
         SELECT DISTINCT m.codigo
           FROM (silver.movimento m
             JOIN gold.fato_processo f_1 USING (registro_id))
        )
 SELECT ((100.0 * (count(*) FILTER (WHERE (tipo_procedimento = 'OUTROS'::text)))::numeric) / (NULLIF(count(*), 0))::numeric) AS tipo_outros_pct,
    ((100.0 * (count(*) FILTER (WHERE (NOT (EXISTS ( SELECT 1
           FROM gold.processo_categoria pc
          WHERE (pc.registro_id = f.registro_id))))))::numeric) / (NULLIF(count(*), 0))::numeric) AS sem_categoria_pct,
    ( SELECT ((100.0 * (count(*) FILTER (WHERE (NOT (EXISTS ( SELECT 1
                   FROM ref.movimento_fase mf
                  WHERE (mf.movimento_codigo = cod.codigo))))))::numeric) / (NULLIF(count(*), 0))::numeric)
           FROM cod) AS movimentos_sem_fase_pct
   FROM gold.fato_processo f;


--
-- Name: qualidade_intensidade_registro; Type: VIEW; Schema: gold; Owner: -
--

CREATE VIEW gold.qualidade_intensidade_registro AS
 SELECT orgao_codigo,
    mesorregiao_id,
    count(*) AS n_processos,
    (avg(n_movimentos))::numeric(12,2) AS media_movimentos,
    percentile_cont((0.5)::double precision) WITHIN GROUP (ORDER BY ((n_movimentos)::double precision)) AS mediana_movimentos
   FROM gold.fato_processo
  GROUP BY orgao_codigo, mesorregiao_id;


--
-- Name: qualidade_movimentos_duplicados; Type: VIEW; Schema: gold; Owner: -
--

CREATE VIEW gold.qualidade_movimentos_duplicados AS
 WITH dup AS (
         SELECT m.registro_id,
            m.codigo,
            m.data_hora
           FROM (silver.movimento m
             JOIN gold.fato_processo f_1 USING (registro_id))
          GROUP BY m.registro_id, m.codigo, m.data_hora
         HAVING (count(*) > 1)
        )
 SELECT f.orgao_codigo,
    count(DISTINCT d.registro_id) AS n_processos,
    count(*) AS n_grupos_duplicados
   FROM (dup d
     JOIN gold.fato_processo f USING (registro_id))
  GROUP BY f.orgao_codigo;


--
-- Name: classe_tipo; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.classe_tipo (
    classe_codigo integer NOT NULL,
    classe_nome text,
    tipo_procedimento text NOT NULL,
    juri boolean NOT NULL
);


--
-- Name: qualidade_sem_mapeamento; Type: VIEW; Schema: gold; Owner: -
--

CREATE VIEW gold.qualidade_sem_mapeamento AS
 SELECT registro_id,
    municipio_sede_ibge,
    classe_codigo,
    (mesorregiao_id IS NULL) AS sem_mesorregiao,
    (NOT (EXISTS ( SELECT 1
           FROM ref.classe_tipo ct
          WHERE (ct.classe_codigo = f.classe_codigo)))) AS classe_fora_ref,
    (NOT (EXISTS ( SELECT 1
           FROM gold.processo_categoria pc
          WHERE (pc.registro_id = f.registro_id)))) AS sem_categoria
   FROM gold.fato_processo f
  WHERE ((mesorregiao_id IS NULL) OR (NOT (EXISTS ( SELECT 1
           FROM ref.classe_tipo ct
          WHERE (ct.classe_codigo = f.classe_codigo)))) OR (NOT (EXISTS ( SELECT 1
           FROM gold.processo_categoria pc
          WHERE (pc.registro_id = f.registro_id)))));


--
-- Name: qualidade_volume_mensal; Type: VIEW; Schema: gold; Owner: -
--

CREATE VIEW gold.qualidade_volume_mensal AS
 SELECT ano_ajuizamento AS ano,
    mes_ajuizamento AS mes,
    tipo_procedimento AS tipo,
    count(*) AS n
   FROM gold.fato_processo
  GROUP BY ano_ajuizamento, mes_ajuizamento, tipo_procedimento;


--
-- Name: assunto_categoria; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.assunto_categoria (
    assunto_codigo integer NOT NULL,
    assunto_nome text,
    categoria text NOT NULL,
    somente_ampliada boolean NOT NULL,
    infracional boolean NOT NULL,
    antecessor boolean NOT NULL
);


--
-- Name: catalogo; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.catalogo (
    codigo integer NOT NULL,
    tipo text NOT NULL,
    grupo text NOT NULL,
    natureza text
);


--
-- Name: cnj_casos_novos; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.cnj_casos_novos (
    ano integer NOT NULL,
    vd_novos integer NOT NULL,
    feminicidio_novos integer NOT NULL,
    mpu integer NOT NULL,
    fonte text
);


--
-- Name: mesorregiao; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.mesorregiao (
    mesorregiao_id integer NOT NULL,
    mesorregiao text NOT NULL,
    n_municipios integer NOT NULL,
    pop_feminina_censo2022 integer,
    geom public.geometry(MultiPolygon,4674)
);


--
-- Name: municipio; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.municipio (
    municipio_ibge integer NOT NULL,
    municipio text NOT NULL,
    mesorregiao_id integer NOT NULL,
    mesorregiao text NOT NULL,
    regiao_intermediaria_id integer,
    regiao_intermediaria text,
    pop_feminina_censo2022 integer,
    geom public.geometry(MultiPolygon,4674)
);


--
-- Name: orgao_especializado; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.orgao_especializado (
    orgao_codigo integer NOT NULL,
    municipio_sede_ibge integer,
    nome_referencia text
);


--
-- Name: quebra_serie; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.quebra_serie (
    categoria text NOT NULL,
    data_inicio date NOT NULL,
    data_fim date,
    tipo text,
    descricao text
);


--
-- Name: identificador; Type: TABLE; Schema: restrito; Owner: -
--

CREATE TABLE restrito.identificador (
    registro_id bigint NOT NULL,
    numero_processo text,
    id_source text,
    ano_numero_cnj smallint
);


--
-- Name: complemento_movimento; Type: TABLE; Schema: silver; Owner: -
--

CREATE TABLE silver.complemento_movimento (
    movimento_id bigint NOT NULL,
    ordem smallint NOT NULL,
    codigo integer,
    descricao text,
    valor integer,
    nome text
);


--
-- Name: movimento_id_seq; Type: SEQUENCE; Schema: silver; Owner: -
--

CREATE SEQUENCE silver.movimento_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: registro; Type: TABLE; Schema: silver; Owner: -
--

CREATE TABLE silver.registro (
    registro_id bigint NOT NULL,
    run_id text NOT NULL,
    api_id text NOT NULL,
    ano_particao smallint NOT NULL,
    pagina integer NOT NULL,
    tribunal text,
    grau text,
    nivel_sigilo smallint,
    classe_codigo integer,
    classe_nome text,
    orgao_codigo integer,
    orgao_nome text,
    municipio_sede_ibge integer,
    data_ajuizamento_original text,
    data_ajuizamento timestamp without time zone,
    data_ultima_atualizacao timestamp with time zone,
    indexado_em timestamp with time zone,
    sistema_codigo smallint,
    sistema_nome text,
    formato_codigo smallint,
    formato_nome text,
    n_movimentos integer NOT NULL,
    hash_source character(64) NOT NULL
);


--
-- Name: registro_assunto; Type: TABLE; Schema: silver; Owner: -
--

CREATE TABLE silver.registro_assunto (
    registro_id bigint NOT NULL,
    posicao smallint NOT NULL,
    assunto_codigo integer NOT NULL,
    nome_original text,
    veio_aninhado boolean NOT NULL
);


--
-- Name: registro_registro_id_seq; Type: SEQUENCE; Schema: silver; Owner: -
--

ALTER TABLE silver.registro ALTER COLUMN registro_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME silver.registro_registro_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: execucao_coleta execucao_coleta_pkey; Type: CONSTRAINT; Schema: controle; Owner: -
--

ALTER TABLE ONLY controle.execucao_coleta
    ADD CONSTRAINT execucao_coleta_pkey PRIMARY KEY (run_id);


--
-- Name: pagina_bronze pagina_bronze_pkey; Type: CONSTRAINT; Schema: controle; Owner: -
--

ALTER TABLE ONLY controle.pagina_bronze
    ADD CONSTRAINT pagina_bronze_pkey PRIMARY KEY (run_id, ano, pagina);


--
-- Name: fato_evento fato_evento_pkey; Type: CONSTRAINT; Schema: gold; Owner: -
--

ALTER TABLE ONLY gold.fato_evento
    ADD CONSTRAINT fato_evento_pkey PRIMARY KEY (registro_id, seq);


--
-- Name: fato_processo fato_processo_pkey; Type: CONSTRAINT; Schema: gold; Owner: -
--

ALTER TABLE ONLY gold.fato_processo
    ADD CONSTRAINT fato_processo_pkey PRIMARY KEY (registro_id);


--
-- Name: processo_categoria processo_categoria_pkey; Type: CONSTRAINT; Schema: gold; Owner: -
--

ALTER TABLE ONLY gold.processo_categoria
    ADD CONSTRAINT processo_categoria_pkey PRIMARY KEY (registro_id, categoria);


--
-- Name: assunto_categoria assunto_categoria_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.assunto_categoria
    ADD CONSTRAINT assunto_categoria_pkey PRIMARY KEY (assunto_codigo);


--
-- Name: catalogo catalogo_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.catalogo
    ADD CONSTRAINT catalogo_pkey PRIMARY KEY (codigo, tipo);


--
-- Name: classe_tipo classe_tipo_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.classe_tipo
    ADD CONSTRAINT classe_tipo_pkey PRIMARY KEY (classe_codigo);


--
-- Name: cnj_casos_novos cnj_casos_novos_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.cnj_casos_novos
    ADD CONSTRAINT cnj_casos_novos_pkey PRIMARY KEY (ano);


--
-- Name: mesorregiao mesorregiao_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.mesorregiao
    ADD CONSTRAINT mesorregiao_pkey PRIMARY KEY (mesorregiao_id);


--
-- Name: movimento_fase movimento_fase_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.movimento_fase
    ADD CONSTRAINT movimento_fase_pkey PRIMARY KEY (movimento_codigo);


--
-- Name: municipio municipio_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.municipio
    ADD CONSTRAINT municipio_pkey PRIMARY KEY (municipio_ibge);


--
-- Name: orgao_especializado orgao_especializado_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.orgao_especializado
    ADD CONSTRAINT orgao_especializado_pkey PRIMARY KEY (orgao_codigo);


--
-- Name: identificador identificador_pkey; Type: CONSTRAINT; Schema: restrito; Owner: -
--

ALTER TABLE ONLY restrito.identificador
    ADD CONSTRAINT identificador_pkey PRIMARY KEY (registro_id);


--
-- Name: complemento_movimento complemento_movimento_pkey; Type: CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.complemento_movimento
    ADD CONSTRAINT complemento_movimento_pkey PRIMARY KEY (movimento_id, ordem);


--
-- Name: movimento movimento_pkey; Type: CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.movimento
    ADD CONSTRAINT movimento_pkey PRIMARY KEY (movimento_id);


--
-- Name: registro_assunto registro_assunto_pkey; Type: CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.registro_assunto
    ADD CONSTRAINT registro_assunto_pkey PRIMARY KEY (registro_id, posicao);


--
-- Name: registro registro_pkey; Type: CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.registro
    ADD CONSTRAINT registro_pkey PRIMARY KEY (registro_id);


--
-- Name: registro registro_run_id_api_id_key; Type: CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.registro
    ADD CONSTRAINT registro_run_id_api_id_key UNIQUE (run_id, api_id);


--
-- Name: movimento_codigo_idx; Type: INDEX; Schema: silver; Owner: -
--

CREATE INDEX movimento_codigo_idx ON silver.movimento USING btree (codigo);


--
-- Name: movimento_registro_idx; Type: INDEX; Schema: silver; Owner: -
--

CREATE INDEX movimento_registro_idx ON silver.movimento USING btree (registro_id);


--
-- Name: registro_api_id_idx; Type: INDEX; Schema: silver; Owner: -
--

CREATE INDEX registro_api_id_idx ON silver.registro USING btree (api_id);


--
-- Name: registro_assunto_codigo_idx; Type: INDEX; Schema: silver; Owner: -
--

CREATE INDEX registro_assunto_codigo_idx ON silver.registro_assunto USING btree (assunto_codigo);


--
-- Name: pagina_bronze pagina_bronze_run_id_fkey; Type: FK CONSTRAINT; Schema: controle; Owner: -
--

ALTER TABLE ONLY controle.pagina_bronze
    ADD CONSTRAINT pagina_bronze_run_id_fkey FOREIGN KEY (run_id) REFERENCES controle.execucao_coleta(run_id);


--
-- Name: identificador identificador_registro_id_fkey; Type: FK CONSTRAINT; Schema: restrito; Owner: -
--

ALTER TABLE ONLY restrito.identificador
    ADD CONSTRAINT identificador_registro_id_fkey FOREIGN KEY (registro_id) REFERENCES silver.registro(registro_id) ON DELETE CASCADE;


--
-- Name: complemento_movimento complemento_movimento_movimento_id_fkey; Type: FK CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.complemento_movimento
    ADD CONSTRAINT complemento_movimento_movimento_id_fkey FOREIGN KEY (movimento_id) REFERENCES silver.movimento(movimento_id) ON DELETE CASCADE;


--
-- Name: movimento movimento_registro_id_fkey; Type: FK CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.movimento
    ADD CONSTRAINT movimento_registro_id_fkey FOREIGN KEY (registro_id) REFERENCES silver.registro(registro_id) ON DELETE CASCADE;


--
-- Name: registro_assunto registro_assunto_registro_id_fkey; Type: FK CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.registro_assunto
    ADD CONSTRAINT registro_assunto_registro_id_fkey FOREIGN KEY (registro_id) REFERENCES silver.registro(registro_id) ON DELETE CASCADE;


--
-- Name: registro registro_run_id_fkey; Type: FK CONSTRAINT; Schema: silver; Owner: -
--

ALTER TABLE ONLY silver.registro
    ADD CONSTRAINT registro_run_id_fkey FOREIGN KEY (run_id) REFERENCES controle.execucao_coleta(run_id);


--
-- PostgreSQL database dump complete
--

