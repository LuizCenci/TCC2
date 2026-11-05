import json

import pytest

from datajud_tcc.bronze import BronzeStore
from datajud_tcc.orquestracao.marca_dagua import MarcaDagua, maior_atualizacao_da_execucao


def _execucao(raiz, datas):
    hits = [
        {"_id": f"id-{i}", "_source": {"dataHoraUltimaAtualizacao": d}, "sort": [f"id-{i}"]}
        for i, d in enumerate(datas)
    ]
    artefato = BronzeStore(raiz).write_page(2024, 1, {"size": 10}, {"hits": {"hits": hits}})
    manifesto = {
        "partitions": {
            "2024": {"artifacts": [{"page": 1, "response": str(artefato.response_path.relative_to(raiz))}]}
        }
    }
    (raiz / "manifest.json").write_text(json.dumps(manifesto), encoding="utf-8")
    return raiz


def test_maior_atualizacao_compara_datas_e_ignora_ausentes(tmp_path):
    datas = ["2026-09-01T10:00:00.000Z", None, "2026-10-05T18:00:31.594Z", "2026-10-05T09:00:00Z"]
    assert maior_atualizacao_da_execucao(_execucao(tmp_path, datas)) == "2026-10-05T18:00:31.594Z"


def test_execucao_sem_registros_nao_tem_marca(tmp_path):
    assert maior_atualizacao_da_execucao(_execucao(tmp_path, [])) is None


def test_marca_dagua_persiste_e_so_avanca(tmp_path):
    marca = MarcaDagua(tmp_path / "estado.json")
    assert marca.ler() is None
    marca.gravar("2026-10-05T18:00:31.594Z", run_id="inc-1")
    assert marca.ler() == "2026-10-05T18:00:31.594Z"
    with pytest.raises(ValueError, match="recuar"):
        marca.gravar("2026-09-01T00:00:00.000Z", run_id="inc-2")
    historico = json.loads((tmp_path / "estado.json").read_text(encoding="utf-8"))["historico"]
    assert [h["run_id"] for h in historico] == ["inc-1"]
