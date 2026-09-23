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
