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
    assert "violência doméstica informados pelo painel do CNJ" in texto
    assert "16,7%" in texto and "21,8%" in texto
    assert "medida protetiva" not in texto
    assert "gold-2026-11-11" in texto


def test_sobre_define_series_por_assuntos():
    at = AppTest.from_file(str(RAIZ / "paginas" / "sobre.py"), default_timeout=30).run()
    assert not at.exception
    texto = " ".join(m.value for m in at.markdown)
    assert "assuntos" in texto
    assert "tipo de procedimento" not in texto


def test_territorio_padrao_acao_penal_2025():
    at = AppTest.from_file(str(RAIZ / "paginas" / "territorio.py"), default_timeout=30).run()
    assert not at.exception
    assert at.selectbox(key="territorio_ano").value == 2025
    assert at.selectbox(key="territorio_tipo").value == "ACAO_PENAL"
    assert any("município-sede" in w.value for w in at.warning)


def test_territorio_taxa_acao_penal_2025_faixa_artigo():
    import sys
    sys.path.insert(0, str(RAIZ))
    from painel import componentes
    t = componentes.tabela("agg_taxa")
    r = t[(t["serie"] == "estrita") & (t["ano_ajuizamento"] == 2025)
          & (t["tipo_procedimento"] == "ACAO_PENAL") & ~t["suprimido"]]
    assert len(r) > 0
    assert 67 <= r["taxa_eb_100k"].min() and r["taxa_eb_100k"].max() <= 237


def test_territorio_recorte_extremo_nao_quebra():
    from painel.exibicao import MSG_TUDO_SUPRIMIDO
    at = AppTest.from_file(str(RAIZ / "paginas" / "territorio.py"), default_timeout=30).run()
    at.selectbox(key="territorio_ano").set_value(2021)
    at.selectbox(key="territorio_tipo").set_value("EXECUCAO").run()
    assert not at.exception
    assert MSG_TUDO_SUPRIMIDO in [i.value for i in at.info]
    assert len(at.get("plotly_chart")) == 1  # só o mapa, sem ranking


def test_volume_jan_ago_ordem_e_suprimidos():
    import json
    at = AppTest.from_file(str(RAIZ / "paginas" / "volume.py"), default_timeout=30).run()
    at.multiselect(key="volume_tipos").select("CARTA").select("EXECUCAO").select("OUTROS").select("RECURSO").run()
    at.radio(key="volume_periodo").set_value("Janeiro a agosto").run()
    assert not at.exception
    assert any(c.value.startswith("Combinações suprimidas") for c in at.caption)
    figs = [json.loads(p.proto.spec) for p in at.get("plotly_chart")]
    jan = [f for f in figs if f["layout"]["title"]["text"] == "Comparação jan–ago entre anos"][0]
    assert jan["layout"]["xaxis"]["categoryarray"][0] == "2019"
    assert jan["layout"]["xaxis"]["categoryarray"][-1] == "2026 (parcial)"


def test_volume_aviso_sobreposicao():
    at = AppTest.from_file(str(RAIZ / "paginas" / "volume.py"), default_timeout=30).run()
    assert not at.exception
    assert any("se sobrepõem" in w.value for w in at.warning)


def test_mpu_mediana_um_dia():
    at = AppTest.from_file(str(RAIZ / "paginas" / "mpu.py"), default_timeout=30).run()
    assert not at.exception
    assert any("1 dia" in m.value for m in at.metric)


def test_mpu_tipos_medida_e_minimo():
    at = AppTest.from_file(str(RAIZ / "paginas" / "mpu.py"), default_timeout=30).run()
    texto = " ".join(c.value for c in list(at.caption) + list(at.markdown))
    assert "mínimo (soma das mesorregiões não suprimidas)" in texto


def test_acoes_penais_coorte_padrao():
    at = AppTest.from_file(str(RAIZ / "paginas" / "acoes_penais.py"), default_timeout=30).run()
    assert not at.exception
    assert at.selectbox(key="ap_coorte").value == "2019-2021"
    assert at.selectbox(key="ap_variante").value == "principal"
    at.selectbox(key="ap_coorte").set_value("2024-2026").run()
    at.selectbox(key="ap_variante").set_value("com_reativados").run()
    assert not at.exception


def test_cobertura_criterio_cnj():
    at = AppTest.from_file(str(RAIZ / "paginas" / "cobertura.py"), default_timeout=30).run()
    assert not at.exception
    texto = " ".join(c.value for c in list(at.markdown) + list(at.caption) + list(at.info))
    assert "critérios do painel do CNJ" in texto
    assert "decisões" in texto and "não são comparadas" in texto
    assert "2019 é anômalo" not in texto and "115" not in texto
    assert "Razão base pública / CNJ (%)" in at.dataframe[0].value.columns


def test_nenhuma_pagina_mostra_taxa_de_violencia():
    for pagina in ["visao_geral", "volume", "territorio", "mpu", "acoes_penais", "cobertura", "sobre"]:
        at = AppTest.from_file(str(RAIZ / "paginas" / f"{pagina}.py"), default_timeout=30).run()
        assert not at.exception, pagina
        elementos = (list(at.markdown) + list(at.caption) + list(at.title) + list(at.header)
                     + list(at.subheader) + list(at.info) + list(at.warning))
        texto = " ".join(e.value for e in elementos).lower()
        assert "taxa de violência" not in texto, pagina
        if pagina not in ("visao_geral", "sobre"):
            assert "vítimas" not in texto, pagina


def _territorio_tipo(tipo=None):
    at = AppTest.from_file(str(RAIZ / "paginas" / "territorio.py"), default_timeout=30).run()
    if tipo:
        at.selectbox(key="territorio_tipo").set_value(tipo).run()
    assert not at.exception
    return at


def test_territorio_tempo_padrao_acao_penal_sentenca():
    at = _territorio_tipo()
    assert at.selectbox(key="territorio_marco_ACAO_PENAL").value == "sentenca"
    tab = at.dataframe[-1].value
    assert len(tab) == 10
    assert tab["Mesorregião"].is_unique


def test_territorio_tempo_mpu_padrao_decisao_mpu():
    at = _territorio_tipo("MPU")
    assert at.selectbox(key="territorio_marco_MPU").value == "decisao_mpu"
    assert len(at.dataframe[-1].value) == 10


def test_territorio_tempo_tipo_sem_marco_mostra_mensagem():
    at = _territorio_tipo("CARTA")
    assert "Não há tempos calculados para este tipo de procedimento. Os tempos existem para ação penal, inquérito e medida protetiva de urgência." in [i.value for i in at.info]
    assert not [s for s in at.selectbox if s.key and s.key.startswith("territorio_marco")]


def test_volume_categorias_usam_contagem_estadual():
    import json
    at = AppTest.from_file(str(RAIZ / "paginas" / "volume.py"), default_timeout=30).run()
    assert not at.exception
    figs = [json.loads(p.proto.spec) for p in at.get("plotly_chart")]
    f = [f for f in figs if f["layout"]["title"]["text"] == "Processos públicos por categoria e ano"][0]
    pares = sum(1 for tr in f["data"] for y in tr["y"] if y is not None)
    assert pares >= 70
    assert any("agg_cautelar.csv" in c.value for c in at.caption)


def test_volume_serie_mensal_marca_2026_parcial():
    import json
    at = AppTest.from_file(str(RAIZ / "paginas" / "volume.py"), default_timeout=30).run()
    figs = [json.loads(p.proto.spec) for p in at.get("plotly_chart")]
    f = [f for f in figs if f["layout"]["title"]["text"] == "Processos públicos ajuizados por mês"][0]
    assert any("2026 parcial" in a.get("text", "") for a in f["layout"].get("annotations", []))
    assert any(s.get("type") == "rect" for s in f["layout"].get("shapes", []))


def test_acoes_penais_cautelar_anos_em_ordem_fixa():
    import json
    at = AppTest.from_file(str(RAIZ / "paginas" / "acoes_penais.py"), default_timeout=30).run()
    assert not at.exception
    figs = [json.loads(p.proto.spec) for p in at.get("plotly_chart")]
    f = [f for f in figs if f["layout"]["title"]["text"].startswith("Resposta cautelar")][0]
    arr = f["layout"]["xaxis"]["categoryarray"]
    assert arr[0] == "2019" and arr[-1] == "2026 (parcial)" and len(arr) == 8


def _figs_volume(at):
    import json
    return [json.loads(p.proto.spec) for p in at.get("plotly_chart")]


def test_volume_padrao_ano_completo_com_2026_parcial():
    at = AppTest.from_file(str(RAIZ / "paginas" / "volume.py"), default_timeout=30).run()
    assert not at.exception
    assert at.radio(key="volume_periodo").value == "Ano completo (2026 parcial)"
    fig = [f for f in _figs_volume(at) if f["layout"]["title"]["text"] == "Processos públicos ajuizados por ano"][0]
    assert "2026 (parcial, jan–set)" in fig["layout"]["xaxis"]["categoryarray"]
    assert any(c.value.startswith("2026 é parcial: ajuizamentos até 30/09/2026, com setembro incompleto; a barra")
               for c in at.caption)


def test_volume_total_anual_bate_com_soma_mensal():
    import sys
    sys.path.insert(0, str(RAIZ))
    from painel import componentes
    at = AppTest.from_file(str(RAIZ / "paginas" / "volume.py"), default_timeout=30).run()
    serie = at.session_state["serie"] if "serie" in at.session_state else "estrita"
    v = componentes.tabela("agg_volume")
    v = v[(v["serie"] == serie) & (v["tipo_procedimento"] == "ACAO_PENAL") & (v["ano_ajuizamento"] == 2025)]
    assert len(v) == 12
    fig = [f for f in _figs_volume(at) if f["layout"]["title"]["text"] == "Processos públicos ajuizados por ano"][0]
    tr = [t for t in fig["data"] if t["name"] == "Ação penal"][0]
    y = dict(zip(tr["x"], tr["y"]))["2025"]
    assert y == int(v["n"].sum())


def test_volume_alternativo_jan_ago():
    at = AppTest.from_file(str(RAIZ / "paginas" / "volume.py"), default_timeout=30).run()
    at.radio(key="volume_periodo").set_value("Janeiro a agosto").run()
    assert not at.exception
    titulos = [f["layout"]["title"]["text"] for f in _figs_volume(at)]
    assert "Comparação jan–ago entre anos" in titulos
    assert "Processos públicos ajuizados por ano" not in titulos
    jan = [f for f in _figs_volume(at) if f["layout"]["title"]["text"] == "Comparação jan–ago entre anos"][0]
    assert "2026 (parcial, jan–set)" not in jan["layout"]["xaxis"]["categoryarray"]


NOTA_FLAGRANTE = ("O código de prisão em flagrante (175) praticamente deixou de ser usado a partir de 2021, "
                  "por isso os valores aparecem suprimidos; no mesmo período cresce o código de flagrante "
                  "convertido em preventiva (12140), contado em \"Prisão preventiva\". "
                  "A série de flagrante não serve para comparar anos após 2020.")


def _linha_ano(tab, ano):
    return tab[tab["Ano de ajuizamento"] == str(ano)].iloc[0]


def test_acoes_penais_tempos_sentenca_numericos():
    import pandas as pd
    at = AppTest.from_file(str(RAIZ / "paginas" / "acoes_penais.py"), default_timeout=30).run()
    assert not at.exception
    tab = at.dataframe[1].value
    assert "Mediana (dias)" in tab.columns
    assert pd.api.types.is_numeric_dtype(tab["Mediana (dias)"])
    assert pd.api.types.is_numeric_dtype(tab["Processos (n, arredondado)"])
    assert _linha_ano(tab, 2019)["Mediana (dias)"] == 1048
    r = _linha_ano(tab, 2025)
    assert pd.isna(r["Mediana (dias)"])
    assert r["Situação"] in ("não estimável", "mediana não alcançada", "suprimido")
    assert _linha_ano(tab, 2019)["Situação"] == ""


def test_mpu_tempos_percentuais_numericos():
    import pandas as pd
    at = AppTest.from_file(str(RAIZ / "paginas" / "mpu.py"), default_timeout=30).run()
    assert not at.exception
    tab = at.dataframe[-1].value
    for c in ["Até 2 dias (%)", "Até 30 dias (%)", "Até 365 dias (%)", "Mediana (dias)",
              "Processos (n, arredondado)"]:
        assert pd.api.types.is_numeric_dtype(tab[c]), c


def test_territorio_tempo_mediana_numerica():
    import pandas as pd
    at = _territorio_tipo()
    tab = at.dataframe[-1].value
    assert len(tab) == 10
    assert pd.api.types.is_numeric_dtype(tab["Mediana (dias)"])
    assert "Situação" in tab.columns


def test_acoes_penais_nota_flagrante():
    at = AppTest.from_file(str(RAIZ / "paginas" / "acoes_penais.py"), default_timeout=30).run()
    assert NOTA_FLAGRANTE in [c.value for c in at.caption]


def test_tabelas_tempo_vazio_em_branco_e_situacao_larga():
    import json
    for pagina in ["acoes_penais", "mpu", "territorio"]:
        at = AppTest.from_file(str(RAIZ / "paginas" / f"{pagina}.py"), default_timeout=30).run()
        assert not at.exception
        pr = at.dataframe[-1].proto
        assert pr.placeholder == "", pagina
        cfg = json.loads(pr.columns)
        assert cfg["Situação"]["width"] == "large", pagina
