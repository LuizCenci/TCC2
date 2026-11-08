import pandas as pd

from painel.exibicao import (formatar_decimal, formatar_inteiro, formatar_pct,
                             rotulo_ano, texto_mediana, valor_ou_suprimido)


def test_formatar_inteiro_de_float():
    assert formatar_inteiro(1234.0) == "1.234"
    assert formatar_inteiro(147020) == "147.020"


def test_formatar_decimal_e_pct():
    assert formatar_decimal(12.345) == "12,3"
    assert formatar_pct(66.887) == "66,9%"
    assert formatar_decimal(1234.56) == "1.234,6"


def test_ausentes():
    for v in (None, pd.NA, float("nan")):
        assert formatar_inteiro(v) == "—"
        assert formatar_decimal(v) == "—"
        assert formatar_pct(v) == "—"
        assert valor_ou_suprimido(v, True) == "suprimido"


def test_valor_ou_suprimido():
    assert valor_ou_suprimido(None, True) == "suprimido"
    assert valor_ou_suprimido(0, False) == "0"


def test_texto_mediana():
    assert texto_mediana(pd.Series({"estimavel": True, "mediana_alcancada": True, "mediana_dias": 758.0, "ic95_inf": 751.0, "ic95_sup": 765.0})) == "758 dias (IC 95%: 751–765)"
    assert texto_mediana(pd.Series({"estimavel": False, "mediana_alcancada": False, "mediana_dias": None, "ic95_inf": None, "ic95_sup": None})) == "não estimável"
    assert texto_mediana(pd.Series({"estimavel": True, "mediana_alcancada": False, "mediana_dias": None, "ic95_inf": None, "ic95_sup": None})) == "mediana não alcançada"


def test_rotulo_ano_parcial():
    assert rotulo_ano(2026, True) == "2026 (parcial)"
    assert rotulo_ano(2025, False) == "2025"
