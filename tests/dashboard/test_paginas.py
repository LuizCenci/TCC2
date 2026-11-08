from pathlib import Path

from streamlit.testing.v1 import AppTest

RAIZ = Path(__file__).resolve().parents[2] / "dashboard"


def test_app_abre_na_visao_geral():
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=30).run()
    assert not at.exception
    assert "147.020" in " ".join(m.value for m in at.metric)


def test_paginas_rodam_sem_erro():
    for pagina in ["visao_geral", "volume", "territorio", "mpu", "acoes_penais", "cobertura", "sobre"]:
        at = AppTest.from_file(str(RAIZ / "paginas" / f"{pagina}.py"), default_timeout=30).run()
        assert not at.exception, pagina


def test_app_para_com_integridade_quebrada(monkeypatch, pasta_copia):
    from painel import config
    with open(pasta_copia / "agg_mpu.csv", "a", encoding="utf-8") as f:
        f.write("adulterado\n")
    monkeypatch.setattr(config, "PASTA_EXPORTACAO", pasta_copia)
    at = AppTest.from_file(str(RAIZ / "app.py"), default_timeout=30).run()
    assert any("agg_mpu.csv" in e.value for e in at.error)
    assert len(at.metric) == 0


def test_visao_geral_metricas_e_rodape():
    at = AppTest.from_file(str(RAIZ / "paginas" / "visao_geral.py"), default_timeout=30).run()
    valores = {m.label: m.value for m in at.metric}
    assert valores["Processos na base analítica"] == "147.020"
    assert "758 dias" in valores["Mediana até a sentença (ação penal)"]
    assert valores["Condenação em 5 anos (ajuizados 2019–2021)"].startswith("46")
    texto = " ".join(c.value for c in at.caption)
    assert "O acervo público reúne de 2,4% a 9,0%" in texto
    assert "gold-2026-11-07" in texto
