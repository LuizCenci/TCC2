from pathlib import Path

from datajud_tcc.catalog import Catalog


CATALOG_PATH = Path("config/catalogs/pvd_cnj_2025-07-17.yaml")


def test_catalog_exposes_all_approved_subject_codes():
    catalog = Catalog.load(CATALOG_PATH)
    assert set(catalog.subject_codes) == {
        10948,
        10949,
        11979,
        12194,
        12196,
        14097,
        14098,
        14226,
        14227,
        14228,
        14229,
        14942,
        14943,
        14944,
        14945,
    }


def test_natures_are_multi_label():
    catalog = Catalog.load(CATALOG_PATH)
    assert catalog.natures_for({10948, 10949}) == frozenset({"civel", "penal"})


VCM_PATH = Path("config/catalogs/tjpr_vcm_2026-10-18.yaml")


def test_vcm_catalog_keeps_pvd_core_and_adds_extensions():
    catalog = Catalog.load(VCM_PATH)
    pvd = Catalog.load(CATALOG_PATH)
    assert catalog.subject_codes == pvd.subject_codes
    assert set(catalog.extension_subject_codes) == {12091, 12358, 15511, 5560, 9647, 14684, 14686}
    assert set(catalog.extension_class_codes) == {1268, 15309, 12423}
    assert catalog.diagnostic_classes == ()


def test_vcm_catalog_groups_extensions():
    catalog = Catalog.load(VCM_PATH)
    groups = {entry.codigo: entry.grupo for entry in catalog.extensions}
    assert groups[1268] == "especifica"
    assert groups[5560] == "ambigua"
    assert groups[14684] == "secundaria"


def test_silver_markers_are_not_selection_codes():
    catalog = Catalog.load(VCM_PATH)
    markers = {12195, 12197, 15174, 15180}
    assert markers.isdisjoint(catalog.subject_codes)
    assert markers.isdisjoint(catalog.extension_subject_codes)


def test_extension_rejects_unknown_group(tmp_path):
    path = tmp_path / "cat.yaml"
    path.write_text(
        VCM_PATH.read_text(encoding="utf-8").replace("grupo: ambigua", "grupo: qualquer", 1),
        encoding="utf-8",
    )
    import pytest

    with pytest.raises(ValueError, match="grupo"):
        Catalog.load(path)


def test_extension_rejects_code_already_in_core(tmp_path):
    path = tmp_path / "cat.yaml"
    path.write_text(
        VCM_PATH.read_text(encoding="utf-8").replace("codigo: 12091,", "codigo: 10949,", 1),
        encoding="utf-8",
    )
    import pytest

    with pytest.raises(ValueError, match="duplicado"):
        Catalog.load(path)
