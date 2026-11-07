CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS ref.municipio (
    municipio_ibge integer PRIMARY KEY,
    municipio text NOT NULL,
    mesorregiao_id integer NOT NULL,
    mesorregiao text NOT NULL,
    regiao_intermediaria_id integer,
    regiao_intermediaria text,
    pop_feminina_censo2022 integer,
    geom geometry(MultiPolygon, 4674)
);

CREATE TABLE IF NOT EXISTS ref.mesorregiao (
    mesorregiao_id integer PRIMARY KEY,
    mesorregiao text NOT NULL,
    n_municipios integer NOT NULL,
    pop_feminina_censo2022 integer,
    geom geometry(MultiPolygon, 4674)
);

CREATE TABLE IF NOT EXISTS ref.classe_tipo (
    classe_codigo integer PRIMARY KEY,
    classe_nome text,
    tipo_procedimento text NOT NULL,
    juri boolean NOT NULL
);
CREATE TABLE IF NOT EXISTS ref.assunto_categoria (
    assunto_codigo integer PRIMARY KEY,
    assunto_nome text,
    categoria text NOT NULL,
    somente_ampliada boolean NOT NULL,
    infracional boolean NOT NULL,
    antecessor boolean NOT NULL
);
CREATE TABLE IF NOT EXISTS ref.movimento_fase (
    movimento_codigo integer PRIMARY KEY,
    movimento_nome text,
    fase text NOT NULL,
    subtipo text
);
CREATE TABLE IF NOT EXISTS ref.orgao_especializado (
    orgao_codigo integer PRIMARY KEY,
    municipio_sede_ibge integer,
    nome_referencia text
);
CREATE TABLE IF NOT EXISTS ref.quebra_serie (
    categoria text NOT NULL,
    data_inicio date NOT NULL,
    data_fim date,
    tipo text,
    descricao text
);
CREATE TABLE IF NOT EXISTS ref.catalogo (
    codigo integer NOT NULL,
    tipo text NOT NULL,
    grupo text NOT NULL,
    natureza text,
    PRIMARY KEY (codigo, tipo)
);

CREATE TABLE IF NOT EXISTS gold.fato_processo (
    registro_id bigint PRIMARY KEY,
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
    data_ajuizamento timestamp,
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

CREATE TABLE IF NOT EXISTS gold.processo_categoria (
    registro_id bigint NOT NULL,
    categoria text NOT NULL,
    somente_ampliada boolean NOT NULL,
    PRIMARY KEY (registro_id, categoria)
);

CREATE TABLE IF NOT EXISTS gold.fato_evento (
    registro_id bigint NOT NULL,
    seq integer NOT NULL,
    dt_evento timestamptz,
    dias_desde_ajuizamento integer,
    movimento_codigo integer,
    fase text NOT NULL,
    subtipo text,
    orgao_codigo integer,
    PRIMARY KEY (registro_id, seq)
);

CREATE TABLE IF NOT EXISTS controle.execucao_gold (
    versao_regras text NOT NULL,
    construida_em timestamptz NOT NULL DEFAULT now(),
    contagens jsonb
);

CREATE TABLE IF NOT EXISTS ref.cnj_casos_novos (
    ano integer PRIMARY KEY,
    vd_novos integer NOT NULL,
    feminicidio_novos integer NOT NULL,
    mpu integer NOT NULL,
    fonte text
);

-- Agregados de contagem (sem identificadores). Reconstruídos por sql/40_agg_contagens.sql.
-- Migração: nomes completos de colunas (só gold.agg_*; reconstruídas pela pipeline).
DROP TABLE IF EXISTS gold.agg_volume;
DROP TABLE IF EXISTS gold.agg_volume_jan_ago;
DROP TABLE IF EXISTS gold.agg_categoria;
DROP TABLE IF EXISTS gold.agg_mpu;
DROP TABLE IF EXISTS gold.agg_mpu_medida;
DROP TABLE IF EXISTS gold.agg_cautelar;
DROP TABLE IF EXISTS gold.agg_qualidade_orgao;
DROP TABLE IF EXISTS gold.agg_cobertura_cnj;
CREATE TABLE IF NOT EXISTS gold.agg_volume (
    pergunta text NOT NULL, ano_ajuizamento integer, ano_parcial boolean, mes_ajuizamento integer, tipo_procedimento text,
    mesorregiao_id integer, serie text NOT NULL, n bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS gold.agg_volume_jan_ago (
    pergunta text NOT NULL, ano_ajuizamento integer, tipo_procedimento text, mesorregiao_id integer, serie text NOT NULL,
    n bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS gold.agg_categoria (
    pergunta text NOT NULL, ano_ajuizamento integer, ano_parcial boolean, tipo_procedimento text, mesorregiao_id integer,
    categoria text, serie text NOT NULL, n bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS gold.agg_mpu (
    pergunta text NOT NULL, ano_ajuizamento integer, ano_parcial boolean, mesorregiao_id integer,
    orgao_especializado boolean, serie text NOT NULL, n bigint NOT NULL,
    n_com_decisao bigint, n_deferimento bigint, n_parcial bigint, n_indeferimento bigint,
    n_revogadas bigint
);
CREATE TABLE IF NOT EXISTS gold.agg_mpu_medida (
    pergunta text NOT NULL, ano_ajuizamento integer, ano_parcial boolean, mesorregiao_id integer,
    tipo_medida text, n bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS gold.agg_cautelar (
    pergunta text NOT NULL, ano_ajuizamento integer, ano_parcial boolean, tipo_procedimento text, categoria text,
    serie text NOT NULL, n bigint NOT NULL, n_flagrante bigint, n_preventiva bigint,
    n_liberdade_provisoria_concedida bigint
);
CREATE TABLE IF NOT EXISTS gold.agg_qualidade_orgao (
    pergunta text NOT NULL, orgao_codigo integer, mesorregiao_id integer, orgao_especializado boolean,
    n bigint NOT NULL, media_movimentos numeric(12,2), mediana_movimentos double precision,
    n_processos_com_duplicado bigint
);
CREATE TABLE IF NOT EXISTS gold.agg_cobertura_cnj (
    pergunta text NOT NULL, ano_ajuizamento integer, ano_parcial boolean, medida text,
    n_base bigint, n_cnj bigint, pct numeric, n bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS gold.agg_pipeline (
    pergunta text NOT NULL, run_id text, concluida_em timestamptz, updated_since text,
    carregada_em timestamptz, versao_regras text, construida_em timestamptz,
    n bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS gold.agg_taxa (
    pergunta text NOT NULL, ano_ajuizamento integer, ano_parcial boolean,
    tipo_procedimento text, serie text NOT NULL, mesorregiao_id integer,
    n bigint NOT NULL, pop_feminina bigint, taxa_bruta_100k double precision,
    taxa_eb_100k double precision
);
