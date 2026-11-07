from datajud_tcc.gold.metodos.supressao import aplicar

G, V = ("ano",), ("v",)


def _l(ano, meso, n):
    return {"ano": ano, "mesorregiao_id": meso, "n": n, "v": n * 10}


def test_supressao_primaria():
    r = aplicar([_l(1, 1, 3), _l(1, 2, 8), _l(1, 3, 9)], limite=5, colunas_grupo=G,
                colunas_valor=V)
    assert r[0]["n"] is None and r[0]["v"] is None and r[0]["suprimido"] is True


def test_supressao_secundaria():
    r = aplicar([_l(1, 1, 3), _l(1, 2, 8), _l(1, 3, 6), _l(2, 1, 7), _l(2, 2, 9)], limite=5,
                colunas_grupo=G, colunas_valor=V)
    assert [x["suprimido"] for x in r] == [True, False, True, False, False]
    assert r[2]["n"] is None and r[2]["v"] is None and r[1]["n"] == 8


def test_supressao_nao_altera_entrada():
    ent = [_l(1, 1, 3), _l(1, 2, 8)]
    copia = [dict(x) for x in ent]
    aplicar(ent, limite=5, colunas_grupo=G, colunas_valor=V)
    assert ent == copia


def test_secundaria_limpa_valores():
    r = aplicar([_l(1, 1, 3), _l(1, 2, 8)], limite=5, colunas_grupo=G, colunas_valor=V)
    assert r[1]["suprimido"] and r[1]["n"] is None and r[1]["v"] is None


def test_subcontagem_com_n_acima_do_limite():
    ent = [{"ano": 1, "n": 20, "a": 3, "b": 9, "est": 0.5}]
    r = aplicar(ent, limite=5, colunas_grupo=G, colunas_valor=("est",), colunas_contagem=("a", "b"))
    assert r[0]["a"] is None and r[0]["b"] == 9 and r[0]["n"] == 20 and r[0]["est"] == 0.5
    assert r[0]["suprimido_parcial"] is True and r[0]["suprimido"] is False


def test_n_none_nao_quebra():
    r = aplicar([{"ano": 1, "n": None, "v": 1}], limite=5, colunas_grupo=G, colunas_valor=V)
    assert r[0]["suprimido"] is True and r[0]["v"] is None
