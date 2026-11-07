import pytest

pytest.importorskip("lifelines")
from lifelines import KaplanMeierFitter  # noqa: E402

from datajud_tcc.gold.metodos.sobrevivencia import estimar_km  # noqa: E402


def test_km_sem_censura_mediana():
    d = list(range(1, 41))
    r = estimar_km(d, [True] * 40)
    ref = KaplanMeierFitter().fit(d, [True] * 40).median_survival_time_
    assert r["estimavel"] and r["mediana_alcancada"]
    assert r["mediana_dias"] == ref and ref in (20, 21)
    assert r["ic95_inf"] is not None


def test_km_estrato_pequeno_nao_estima():
    r = estimar_km(list(range(1, 30)), [True] * 29)
    assert r["n"] == 29 and r["n_eventos"] == 29 and not r["estimavel"]
    assert r["mediana_dias"] is None and r["pct_evento_ate_30"] is None


def test_km_mediana_nao_alcancada():
    r = estimar_km(list(range(1, 41)), [True] * 15 + [False] * 25)
    assert r["estimavel"] and r["mediana_dias"] is None and r["mediana_alcancada"] is False
    assert r["n_eventos"] == 15


def test_km_pct_ate_horizonte():
    r = estimar_km(list(range(1, 41)), [True] * 40)
    assert r["pct_evento_ate_2"] == pytest.approx(5.0)
    assert r["pct_evento_ate_30"] == pytest.approx(75.0)
    assert r["pct_evento_ate_365"] == pytest.approx(100.0)
