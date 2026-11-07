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
