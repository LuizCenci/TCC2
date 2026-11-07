"""Gera config/gold/*.csv a partir das evidências (UTF-8, LF, ordenado por código)."""

import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVID = RAIZ / "docs/artigo/evidencias/referencias_gold_20261107"
SAIDA = RAIZ / "config/gold"


def _json(nome):
    return json.loads((EVID / nome).read_text(encoding="utf-8"))


def _csv(nome, colunas, linhas):
    with open(SAIDA / nome, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=colunas, lineterminator="\n")
        w.writeheader()
        w.writerows(linhas)


def classes():
    fonte = "SGT/CNJ, hierarquia da TPU (21 §5.1)"
    linhas = []
    for c in _json("proposta_ref_classe_tipo.json"):
        cod = c["classe_codigo"]
        tipo = "OUTROS" if cod == 11037 else c["tipo_procedimento"]
        linhas.append({"classe_codigo": cod, "classe_nome": c["nome"],
                       "tipo_procedimento": tipo,
                       "juri": "true" if cod == 282 else "false", "fonte": fonte})
    linhas.sort(key=lambda l: l["classe_codigo"])
    _csv("ref_classe_tipo.csv",
         ["classe_codigo", "classe_nome", "tipo_procedimento", "juri", "fonte"], linhas)


EXPLICITAS = {
    "FISICA": [12194, 14943, 12196, 14945, 3386, 5556, 5557, 11238, 11237, 10842, 9642, 12345, 5560, 9647],
    "PSICOLOGICA": [14942, 14944],
    "AMEACA": [3402, 9661, 11253],
    "PERSEGUICAO": [14684, 14686, 12354],
    "DESCUMPRIMENTO_MPU": [14227, 14229],
    "FEMINICIDIO": [12091],
}
SOMENTE_AMPLIADA = {5560, 9647}
ANTECESSOR = {12354}
HIERARQUIA = [("SEXUAL", "Dignidade Sexual"), ("PATRIMONIAL", "Patrimônio"), ("MORAL", "Honra")]


def assuntos():
    explicito = {c: cat for cat, cs in EXPLICITAS.items() for c in cs}
    linhas = []
    for a in _json("codigos_silver_sgt.json")["assuntos"]:
        cod = a["codigo"]
        nome = a.get("nome_sgt") or a["nome_api"]
        nomes = [nome] + [h["nome"] for h in a["hierarquia"]]
        cat = explicito.get(cod)
        fonte = "lista explícita (21 §5.2)"
        if cat is None:
            for categoria, termo in HIERARQUIA:
                if not any(termo in n for n in nomes):
                    continue
                if categoria == "PATRIMONIAL" and (
                        cod == 14698 or any("Patrimônio Genético" in n for n in nomes)):
                    continue
                cat = categoria
                fonte = f"hierarquia SGT: '{termo}' (21 §5.2)"
                break
        if cat is None:
            continue
        infr = any("DIREITO DA CRIANÇA E DO ADOLESCENTE" in n for n in nomes)
        linhas.append({
            "assunto_codigo": cod, "assunto_nome": nome, "categoria": cat,
            "somente_ampliada": "true" if cod in SOMENTE_AMPLIADA else "false",
            "infracional": "true" if infr else "false",
            "antecessor": "true" if cod in ANTECESSOR else "false",
            "fonte": fonte})
    linhas.sort(key=lambda l: l["assunto_codigo"])
    _csv("ref_assunto_categoria.csv",
         ["assunto_codigo", "assunto_nome", "categoria", "somente_ampliada",
          "infracional", "antecessor", "fonte"], linhas)


FASES = {
    "DISTRIBUICAO": [26],
    "REDISTRIBUICAO": [36, 12646, 12255],
    "DECISAO_MPU": [11423, 11424, 11425],
    "MPU_REVOGACAO": [11426],
    "MPU_PRORROGACAO": [14733],
    "RECEBIMENTO_DENUNCIA": [391, 393, 388],
    "REJEICAO_DENUNCIA": [402, 404],
    "AUDIENCIA": [12750, 12749, 12742, 12745, 12753, 12743, 12741, 12747, 15188,
                  12740, 12744, 12739, 12752, 313],
    "SENTENCA_CONDENATORIA": [219, 221],
    "SENTENCA_ABSOLUTORIA": [220, 11876, 11877],
    "EXTINCAO_PUNIBILIDADE": [11879, 1042, 1046, 11411, 1047, 1050, 1043, 1044, 12735, 1049, 12028],
    "PRESCRICAO": [11878, 471],
    "SENTENCA_OUTRA": [461, 460, 463, 459, 12459, 455, 11376],
    "PRONUNCIA": [10953],
    "IMPRONUNCIA": [10961],
    "TRANSITO_JULGADO": [848],
    "ARQUIVAMENTO_INVESTIGACAO": [12430, 1063],
    "ARQUIVAMENTO": [246, 245],
    "REATIVACAO": [849, 893],
    "CAUTELAR_PRISAO": [175, 12140, 15032, 128, 12141, 146, 12148],
    "LIBERDADE_PROVISORIA": [818, 12146],
    "SUSPENSAO": [264, 12737, 263, 898, 12733],
    "TRAMITACAO_DIRETA": [14999, 15000],
}
SUBTIPOS = {11423: "DEFERIMENTO", 11424: "PARCIAL", 11425: "INDEFERIMENTO",
            219: "TOTAL", 221: "PARCIAL", 12750: "INSTRUCAO_JULGAMENTO",
            12749: "INSTRUCAO", 12742: "CUSTODIA", 12745: "ART16_LMP",
            246: "DEFINITIVO", 245: "PROVISORIO"}


def movimentos():
    nomes = {m["codigo"]: m.get("nome_sgt") or m["nome_api"]
             for m in _json("codigos_silver_sgt.json")["movimentos"]}
    nomes[391] = "Denúncia"  # consulta ao SGT falhou (HTTP 502)
    linhas = []
    for fase, codigos in FASES.items():
        for c in codigos:
            if c not in nomes:
                raise SystemExit(f"movimento {c} ausente das evidências")
            linhas.append({"movimento_codigo": c, "movimento_nome": nomes[c], "fase": fase,
                           "subtipo": SUBTIPOS.get(c, ""),
                           "fonte": "21 §5.3; nome SGT/CNJ"})
    linhas.sort(key=lambda l: l["movimento_codigo"])
    _csv("ref_movimento_fase.csv",
         ["movimento_codigo", "movimento_nome", "fase", "subtipo", "fonte"], linhas)


def orgaos():
    vistos = {}
    for o in _json("orgaos_especializados_silver.json"):
        cod = o["orgao_codigo"]
        if cod not in vistos or o["registros"] > vistos[cod]["registros"]:
            vistos[cod] = o  # nome de referência: variante com mais registros
    linhas = [{"orgao_codigo": c, "municipio_sede_ibge": o["municipio_sede_ibge"],
               "nome_referencia": o["orgao_nome"],
               "fonte": "Nome oficial do órgão na API; conferido com Guia CEVID-TJPR 2021"}
              for c, o in sorted(vistos.items())]
    _csv("ref_orgao_especializado.csv",
         ["orgao_codigo", "municipio_sede_ibge", "nome_referencia", "fonte"], linhas)


def municipios():
    dados = sorted(_json("ref_municipio_pr.json"), key=lambda m: m["municipio_ibge"])
    colunas = list(dados[0].keys())
    fonte = "IBGE Localidades + SIDRA 9514 (Censo 2022), 07/11/2026"
    _csv("ref_municipio_pr.csv", colunas + ["fonte"], [{**m, "fonte": fonte} for m in dados])


def quebras():
    dados = [
        ("PERSEGUICAO", "2021-04-01", "lei", "Lei 14.132/2021"),
        ("PSICOLOGICA", "2021-07-29", "lei", "Lei 14.188/2021"),
        ("FISICA", "2021-07-29", "lei", "Lei 14.188/2021, art. 129 §13"),
        ("FEMINICIDIO", "2024-10-10", "lei", "Lei 14.994/2024, art. 121-A"),
        ("DESCUMPRIMENTO_MPU", "2024-10-10", "lei", "Lei 14.994/2024"),
        ("FISICA", "2021-01-01", "tpu", "Transição 5560 → 12194/14943, 07 §8"),
        ("TODAS", "2019-01-01 a 2020-12-31", "registro", "Anomalias de registro, 08 §7"),
    ]
    fonte = "docs/artigo/21-fontes-referencia-gold.md §2"
    linhas = [{"categoria": c, "data": d, "tipo": t, "descricao": s, "fonte": fonte}
              for c, d, t, s in dados]
    _csv("ref_quebras_serie.csv", ["categoria", "data", "tipo", "descricao", "fonte"], linhas)


if __name__ == "__main__":
    SAIDA.mkdir(parents=True, exist_ok=True)
    classes()
    assuntos()
    movimentos()
    orgaos()
    municipios()
    quebras()
