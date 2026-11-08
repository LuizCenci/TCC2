from datajud_tcc.gold.metodos.exportacao import _escrever_csv, _escrever_manifesto


def test_arquivos_exportados_usam_lf(tmp_path):
    csv_p = tmp_path / "t.csv"
    _escrever_csv(csv_p, ["a", "b"], [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
    man_p = tmp_path / "manifesto.json"
    _escrever_manifesto(man_p, {"k": [1, 2]})
    assert b"\r\n" not in csv_p.read_bytes()
    assert csv_p.read_bytes().startswith(b"a,b\n")
    assert b"\r\n" not in man_p.read_bytes()
