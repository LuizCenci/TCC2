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
