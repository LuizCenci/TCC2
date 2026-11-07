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
