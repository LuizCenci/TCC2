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
    r = estimar_km(list(range(1, 81)), [True] * 80)
    assert r["pct_evento_ate_2"] == pytest.approx(2.5)
    assert r["pct_evento_ate_30"] == pytest.approx(37.5)
    assert r["pct_evento_ate_365"] is None  # além do seguimento


def test_km_horizonte_com_um_censurado_longo_e_nulo():
    dur = [1] * 40 + [800]
    r = estimar_km(dur, [True] * 40 + [False])
    assert r["pct_evento_ate_730"] is None  # 1 em risco
    assert r["pct_evento_ate_2"] is None  # só 1 com duração >= 2


def test_km_risco_minimo_30():
    def pct(n_longos):
        dur = [1] * 10 + [730] * n_longos
        return estimar_km(dur, [True] * 10 + [False] * n_longos)["pct_evento_ate_730"]
    assert pct(30) is not None
    assert pct(29) is None
