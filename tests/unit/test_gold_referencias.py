from pathlib import Path

import pytest

from datajud_tcc.gold import referencias as r


def test_regras_versao():
    assert r.ler_regras()["versao_regras"] == "gold-2026-11-11"


def test_classes_cobrem_67_e_tipos_validos():
    l = r.ler_csv("ref_classe_tipo.csv")
    assert len(l) == 67
    assert all(x["tipo_procedimento"] in r.TIPOS for x in l)
    por = {x["classe_codigo"]: x for x in l}
    assert por["11037"]["tipo_procedimento"] == "OUTROS"
    assert [x["classe_codigo"] for x in l if x["juri"] == "true"] == ["282"]


def test_categorias_validas_e_unicas():
    l = r.ler_csv("ref_assunto_categoria.csv")
    cods = [x["assunto_codigo"] for x in l]
    assert len(cods) == len(set(cods))
    assert all(x["categoria"] in r.CATEGORIAS for x in l)
    por = {x["assunto_codigo"]: x for x in l}
    assert por["5560"]["somente_ampliada"] == "true"
    assert por["9647"]["somente_ampliada"] == "true"
    assert por["12354"]["antecessor"] == "true"
    assert "14698" not in por
    assert por["3465"]["categoria"] == "SEXUAL"
    assert por["3426"]["categoria"] == "PATRIMONIAL"
    assert por["12544"]["categoria"] == "MORAL"


def test_fases_validas():
    l = r.ler_csv("ref_movimento_fase.csv")
    assert all(x["fase"] in r.FASES for x in l)
    por = {x["movimento_codigo"]: x for x in l}
    for c, s in (("11423", "DEFERIMENTO"), ("11424", "PARCIAL"), ("11425", "INDEFERIMENTO")):
        assert (por[c]["fase"], por[c]["subtipo"]) == ("DECISAO_MPU", s)
    assert (por["246"]["fase"], por["246"]["subtipo"]) == ("ARQUIVAMENTO", "DEFINITIVO")
    assert (por["12745"]["fase"], por["12745"]["subtipo"]) == ("AUDIENCIA", "ART16_LMP")
    assert por["391"]["movimento_nome"] == "Denúncia"


def test_municipios_399_e_10_mesorregioes():
    l = r.ler_csv("ref_municipio_pr.csv")
    assert len(l) == 399
    assert len({x["mesorregiao_id"] for x in l}) == 10
    assert sum(int(x["pop_feminina_censo2022"]) for x in l) == 5867030


def test_orgaos_especializados_12():
    l = r.ler_csv("ref_orgao_especializado.csv")
    assert len(l) == 12
    assert len({x["orgao_codigo"] for x in l}) == 12


def test_validar_aceita_arquivos_do_repositorio():
    r.validar()
    with pytest.raises(ValueError):
        r.validar(Path("config/gold_inexistente"))


def test_hierarquia_sem_caixa_e_infracional():
    por = {x["assunto_codigo"]: x for x in r.ler_csv("ref_assunto_categoria.csv")}
    assert por["12384"]["categoria"] == "SEXUAL" and por["12384"]["infracional"] == "true"
    assert por["9642"]["infracional"] == "true"
    assert por["3465"]["infracional"] == "false"
    assert len(r.ler_csv("ref_quebras_serie.csv")) == 7


def test_ler_regras_independe_do_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert r._dir_padrao().exists()
    assert r.ler_regras(r._dir_padrao())["versao_regras"] == "gold-2026-11-11"
