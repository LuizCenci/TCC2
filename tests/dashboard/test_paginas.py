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
    assert not at.exception
    valores = {m.label: m.value for m in at.metric}
    assert valores["Processos na base"] == "147.020"
    assert valores["Mediana até a sentença"] == "758 dias"
    assert valores["Mediana até decisão da MPU"] == "1 dia"
    assert valores["Condenação em 5 anos"].startswith("46")
    for v in valores.values():
        assert "…" not in v and len(v) <= 12
    texto = " ".join(c.value for c in at.caption)
    assert "Nos anos completos de 2020 a 2025" in texto
    assert "2,7% a 6,0%" in texto
    assert "gold-2026-11-07" in texto


def test_sobre_define_series_por_assuntos():
    at = AppTest.from_file(str(RAIZ / "paginas" / "sobre.py"), default_timeout=30).run()
    assert not at.exception
    texto = " ".join(m.value for m in at.markdown)
    assert "assuntos" in texto
    assert "tipo de procedimento" not in texto
