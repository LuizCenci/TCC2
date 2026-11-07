import random

import pytest

pytest.importorskip("lifelines")

from datajud_tcc.gold.metodos.sobrevivencia import incidencia_acumulada  # noqa: E402


def _dados(n=60, censura=True):
    rnd = random.Random(1)
    dur = rnd.sample(range(10, 3000), n)
    causas = [rnd.choice([0, 1, 2, 3] if censura else [1, 2, 3]) for _ in range(n)]
    return dur, causas


def test_ia_soma_menor_ou_igual_100():
    dur, causas = _dados()
    r = incidencia_acumulada(dur, causas)
    for h in (365, 730, 1095, 1825):
        assert sum(r[k][h] for k in r if r[k][h] is not None) <= 100 + 1e-9


def test_ia_sem_censura_igual_proporcao():
    dur, causas = _dados(censura=False)
    h = max(dur)
    r = incidencia_acumulada(dur, causas, horizontes=(h,))
    for k in (1, 2, 3):
        assert r[k][h] == pytest.approx(100 * causas.count(k) / len(causas), abs=1e-6)


def test_ia_estrato_pequeno():
    assert incidencia_acumulada(list(range(1, 29)), [1] * 28) == {}


def test_ia_horizonte_alem_do_observado_e_nulo():
    dur, causas = _dados()
    r = incidencia_acumulada(dur, causas, horizontes=(10**6,))
    assert all(r[k][10**6] is None for k in r)


def test_ia_empates_soma_igual_km():
    from lifelines import KaplanMeierFitter

    rnd = random.Random(0)
    dur = rnd.choices(range(1, 40), k=200)
    causas = rnd.choices([0, 1, 2, 3], k=200)
    hs = (1, 5, 10, 20, 39)
    r = incidencia_acumulada(dur, causas, horizontes=hs)
    km = KaplanMeierFitter().fit(dur, [c != 0 for c in causas])
    for h in hs:
        s = float(km.survival_function_at_times(h).iloc[0])
        assert sum(r[k][h] for k in r) == pytest.approx(100 * (1 - s), abs=1e-9)


def test_ia_caso_manual_com_empates():
    # 30 observações: t=1: 10 em risco... construído: 10 de causa 1 e 10 de causa 2 em t=1,
    # 10 censuras em t=2. n(1)=30, d1=10, d2=10 -> CIF1(1)=10/30, CIF2(1)=10/30; depois só censura.
    dur = [1] * 20 + [2] * 10
    causas = [1] * 10 + [2] * 10 + [0] * 10
    r = incidencia_acumulada(dur, causas, horizontes=(1, 2))
    assert r[1][1] == pytest.approx(100 / 3, abs=1e-9)
    assert r[2][1] == pytest.approx(100 / 3, abs=1e-9)
    assert r[1][2] == pytest.approx(100 / 3, abs=1e-9)
