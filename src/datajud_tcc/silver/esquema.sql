CREATE SCHEMA IF NOT EXISTS controle; CREATE SCHEMA IF NOT EXISTS silver; CREATE SCHEMA IF NOT EXISTS restrito;

CREATE TABLE IF NOT EXISTS controle.execucao_coleta (
  run_id text PRIMARY KEY, catalogo_versao text, catalogo_sha256 char(64), config_hash char(64),
  versao_coletor text, updated_since text, status_coleta text, criada_em timestamptz, concluida_em timestamptz,
  carregada_em timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS controle.pagina_bronze (
  run_id text REFERENCES controle.execucao_coleta, ano smallint, pagina int, sha256 char(64) NOT NULL,
  n_registros int NOT NULL, total_api int, PRIMARY KEY (run_id, ano, pagina));

CREATE TABLE IF NOT EXISTS silver.registro (
  registro_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id text NOT NULL REFERENCES controle.execucao_coleta, api_id text NOT NULL, ano_particao smallint NOT NULL, pagina int NOT NULL,
  tribunal text, grau text, nivel_sigilo smallint,
  classe_codigo int, classe_nome text, orgao_codigo int, orgao_nome text, municipio_sede_ibge int,
  data_ajuizamento_original text, data_ajuizamento timestamp, data_ultima_atualizacao timestamptz, indexado_em timestamptz,
  sistema_codigo smallint, sistema_nome text, formato_codigo smallint, formato_nome text,
  n_movimentos int NOT NULL, hash_source char(64) NOT NULL, UNIQUE (run_id, api_id));
CREATE TABLE IF NOT EXISTS restrito.identificador (
  registro_id bigint PRIMARY KEY REFERENCES silver.registro ON DELETE CASCADE,
  numero_processo text, id_source text, ano_numero_cnj smallint);
CREATE TABLE IF NOT EXISTS silver.registro_assunto (
  registro_id bigint REFERENCES silver.registro ON DELETE CASCADE, posicao smallint,
  assunto_codigo int NOT NULL, nome_original text, veio_aninhado boolean NOT NULL, PRIMARY KEY (registro_id, posicao));
CREATE TABLE IF NOT EXISTS silver.movimento (
  movimento_id bigint PRIMARY KEY, registro_id bigint NOT NULL REFERENCES silver.registro ON DELETE CASCADE,
  codigo int, nome_original text, data_hora timestamptz, dias_desde_ajuizamento int,
  orgao_codigo_original text, orgao_codigo int, orgao_nome text, ordem_original int NOT NULL, ordem_cronologica int NOT NULL);
CREATE SEQUENCE IF NOT EXISTS silver.movimento_id_seq;
CREATE TABLE IF NOT EXISTS silver.complemento_movimento (
  movimento_id bigint REFERENCES silver.movimento ON DELETE CASCADE, ordem smallint,
  codigo int, descricao text, valor int, nome text, PRIMARY KEY (movimento_id, ordem));
CREATE INDEX IF NOT EXISTS movimento_registro_idx ON silver.movimento (registro_id);
CREATE INDEX IF NOT EXISTS movimento_codigo_idx ON silver.movimento (codigo);
CREATE INDEX IF NOT EXISTS registro_assunto_codigo_idx ON silver.registro_assunto (assunto_codigo);
CREATE INDEX IF NOT EXISTS registro_api_id_idx ON silver.registro (api_id);
