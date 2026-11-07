# Levanta classes, assuntos e movimentos presentes na base de análise (Silver) e
# os enriquece com nome oficial e hierarquia do webservice público SGT/CNJ.
# Saída só com códigos e contagens agregadas (sem identificadores de processo).
# Uso (raiz do projeto, .venv): python docs/artigo/evidencias/scripts/referencias_gold.py SAIDA.json
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sgt import parents, item  # mesmo cliente SOAP usado em sgt_tpu_20261018
from datajud_tcc.silver.conexao import conectar

BASE = ("(select * from silver.registro where (run_id='bronze-20261018-9852486' and ano_particao<2026)"
        " or run_id='bronze2026-20261105-b67187c')")
MIN_MOV_REGISTROS = 20  # movimentos presentes em pelo menos 20 registros

def silver():
    with conectar() as c:
        q = lambda s: c.execute(s).fetchall()
        classes = q(f"select classe_codigo, min(classe_nome), count(*) from {BASE} r group by 1 order by 3 desc")
        assuntos = q(f"select a.assunto_codigo, min(a.nome_original), count(distinct r.registro_id) from {BASE} r "
                     "join silver.registro_assunto a using(registro_id) group by 1 order by 3 desc")
        movs = q(f"select m.codigo, min(m.nome_original), count(distinct m.registro_id), count(*) from {BASE} r "
                 "join silver.movimento m using(registro_id) where m.codigo is not null group by 1 "
                 f"having count(distinct m.registro_id) >= {MIN_MOV_REGISTROS} order by 3 desc")
        total = q(f"select count(*) from {BASE} r")[0][0]
    return total, classes, assuntos, movs

_nomes = {}
def nome(code, tabela):
    k = (code, tabela)
    if k not in _nomes:
        _nomes[k] = item(code, tabela).get("nome")
    return _nomes[k]

def enriquecer(code, tabela):
    try:
        ps = parents(code, tabela)
        return {"nome_sgt": nome(code, tabela), "hierarquia": [{"codigo": p, "nome": nome(p, tabela)} for p in ps if p != code]}
    except Exception as e:  # registra a falha, não inventa
        return {"erro_sgt": f"{type(e).__name__}: {e}"}

if __name__ == "__main__":
    total, classes, assuntos, movs = silver()
    out = {"base_registros": total, "criterio_movimentos": f">= {MIN_MOV_REGISTROS} registros", "classes": [], "assuntos": [], "movimentos": []}
    for c, n, k in classes:
        out["classes"].append({"codigo": c, "nome_api": n, "registros": k, **(enriquecer(c, "C") if c and c > 0 else {})})
        print("C", c, k, flush=True)
    for c, n, k in assuntos:
        out["assuntos"].append({"codigo": c, "nome_api": n, "registros": k, **enriquecer(c, "A")})
        print("A", c, k, flush=True)
    for c, n, k, m in movs:
        out["movimentos"].append({"codigo": c, "nome_api": n, "registros": k, "ocorrencias": m, **enriquecer(c, "M")})
        print("M", c, k, flush=True)
    json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("ok", len(out["classes"]), len(out["assuntos"]), len(out["movimentos"]))
