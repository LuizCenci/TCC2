import pytest

from datajud_tcc.gold.metodos.taxas import bayes_empirico_global


def test_eb_sem_variancia_puxa_para_media():
    r = bayes_empirico_global([10, 20, 30], [1000, 2000, 3000])
    assert r == pytest.approx([0.01, 0.01, 0.01], abs=1e-12)


def test_eb_area_pequena_encolhe_mais():
    casos, pop = [2, 300, 1500], [100, 10000, 100000]
    m = sum(casos) / sum(pop)
    eb = bayes_empirico_global(casos, pop)
    assert abs(eb[0] - m) / abs(casos[0] / pop[0] - m) < abs(eb[2] - m) / abs(casos[2] / pop[2] - m)


def test_eb_populacao_zero():
    eb = bayes_empirico_global([5, 3, 0], [1000, 0, 0])
    assert eb[1] is None and eb[2] is None
    assert eb[0] == pytest.approx(0.005)


def test_eb_valores_conhecidos():
    # P=[1000,3000], n=[50,30]: m=.02; s2=3e-4-.02/2000=2.9e-4; C=[2.9/3.1, 870/890]
    eb = bayes_empirico_global([50, 30], [1000, 3000])
    assert eb[0] == pytest.approx(0.02 + (2.9 / 3.1) * 0.03, abs=1e-9)
    assert eb[1] == pytest.approx(0.02 - (870 / 890) * 0.01, abs=1e-9)
    assert eb[0] == pytest.approx(0.0480645161, abs=1e-9)
    assert eb[1] == pytest.approx(0.0102247191, abs=1e-9)


def test_eb_casos_zero():
    assert bayes_empirico_global([0, 0], [1000, 2000]) == [0.0, 0.0]
