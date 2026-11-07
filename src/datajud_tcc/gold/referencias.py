"""Leitura e validação das referências versionadas da Gold."""

import csv
from pathlib import Path

import yaml

def _dir_padrao() -> Path:
    local = Path("config/gold")
    if local.exists():
        return local
    return Path(__file__).resolve().parents[3] / "config" / "gold"


DIR_PADRAO = _dir_padrao()

TIPOS = ("MPU", "INQUERITO", "ACAO_PENAL", "CARTA", "CAUTELAR_INCIDENTE",
         "RECURSO", "EXECUCAO", "OUTROS")
CATEGORIAS = ("FISICA", "PSICOLOGICA", "AMEACA", "PERSEGUICAO", "SEXUAL",
              "PATRIMONIAL", "MORAL", "DESCUMPRIMENTO_MPU", "FEMINICIDIO",
              "VD_SEM_ESPECIFICACAO")
FASES = ("DISTRIBUICAO", "REDISTRIBUICAO", "DECISAO_MPU", "MPU_REVOGACAO",
         "MPU_PRORROGACAO", "RECEBIMENTO_DENUNCIA", "REJEICAO_DENUNCIA",
         "AUDIENCIA", "SENTENCA_CONDENATORIA", "SENTENCA_ABSOLUTORIA",
         "EXTINCAO_PUNIBILIDADE", "PRESCRICAO", "SENTENCA_OUTRA", "PRONUNCIA",
         "IMPRONUNCIA", "TRANSITO_JULGADO", "ARQUIVAMENTO_INVESTIGACAO",
         "ARQUIVAMENTO", "REATIVACAO", "CAUTELAR_PRISAO",
         "LIBERDADE_PROVISORIA", "SUSPENSAO", "TRAMITACAO_DIRETA")


def ler_regras(dir: Path = DIR_PADRAO) -> dict:
    with open(Path(dir) / "regras.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ler_csv(nome: str, dir: Path = DIR_PADRAO) -> list[dict]:
    with open(Path(dir) / nome, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def validar(dir: Path = DIR_PADRAO) -> None:
    problemas: list[str] = []
    try:
        regras = ler_regras(dir)
    except FileNotFoundError:
        raise ValueError(f"regras.yaml ausente em {dir}")
    for nome in regras["arquivos"]:
        if not (Path(dir) / nome).exists():
            problemas.append(f"arquivo ausente: {nome}")
    if problemas:
        raise ValueError("; ".join(problemas))

    def checar(nome, coluna_codigo, coluna_valor, validos):
        vistos = set()
        for l in ler_csv(nome, dir):
            if l[coluna_codigo] in vistos:
                problemas.append(f"{nome}: código repetido {l[coluna_codigo]}")
            vistos.add(l[coluna_codigo])
            if l[coluna_valor] not in validos:
                problemas.append(f"{nome}: {coluna_valor} inválido em {l[coluna_codigo]}")

    checar("ref_classe_tipo.csv", "classe_codigo", "tipo_procedimento", TIPOS)
    checar("ref_assunto_categoria.csv", "assunto_codigo", "categoria", CATEGORIAS)
    checar("ref_movimento_fase.csv", "movimento_codigo", "fase", FASES)
    if len(ler_csv("ref_municipio_pr.csv", dir)) != 399:
        problemas.append("ref_municipio_pr.csv: esperado 399 municípios")
    if problemas:
        raise ValueError("; ".join(problemas))


def _bool(v: str) -> bool:
    return v.strip().lower() == "true"


def _int_ou_none(v: str):
    return int(v) if v.strip() else None


def _caminho_catalogo(caminho: str, dir: Path) -> Path:
    p = Path(caminho)
    if p.exists():
        return p
    alt = Path(dir).resolve().parent.parent / caminho
    return alt if alt.exists() else p


def carregar_referencias(conn, dir: Path = DIR_PADRAO) -> dict[str, int]:
    """TRUNCATE + carga das ref.* (exceto municipio/mesorregiao); sem commit."""
    from datajud_tcc.catalog import Catalog

    def carga(tabela, colunas, linhas):
        conn.execute(f"TRUNCATE {tabela}")
        if linhas:
            ph = ",".join(["%s"] * len(colunas))
            with conn.cursor() as cur:
                cur.executemany(
                    f"INSERT INTO {tabela} ({','.join(colunas)}) VALUES ({ph})", linhas)
        return len(linhas)

    n: dict[str, int] = {}
    n["classe_tipo"] = carga(
        "ref.classe_tipo", ["classe_codigo", "classe_nome", "tipo_procedimento", "juri"],
        [(int(l["classe_codigo"]), l["classe_nome"], l["tipo_procedimento"], _bool(l["juri"]))
         for l in ler_csv("ref_classe_tipo.csv", dir)])
    n["assunto_categoria"] = carga(
        "ref.assunto_categoria",
        ["assunto_codigo", "assunto_nome", "categoria", "somente_ampliada",
         "infracional", "antecessor"],
        [(int(l["assunto_codigo"]), l["assunto_nome"], l["categoria"],
          _bool(l["somente_ampliada"]), _bool(l["infracional"]), _bool(l["antecessor"]))
         for l in ler_csv("ref_assunto_categoria.csv", dir)])
    n["movimento_fase"] = carga(
        "ref.movimento_fase", ["movimento_codigo", "movimento_nome", "fase", "subtipo"],
        [(int(l["movimento_codigo"]), l["movimento_nome"], l["fase"], l["subtipo"] or None)
         for l in ler_csv("ref_movimento_fase.csv", dir)])
    n["orgao_especializado"] = carga(
        "ref.orgao_especializado", ["orgao_codigo", "municipio_sede_ibge", "nome_referencia"],
        [(int(l["orgao_codigo"]), _int_ou_none(l["municipio_sede_ibge"]), l["nome_referencia"])
         for l in ler_csv("ref_orgao_especializado.csv", dir)])

    quebras = []
    for l in ler_csv("ref_quebras_serie.csv", dir):
        ini, _, fim = l["data"].partition(" a ")
        quebras.append((l["categoria"], ini.strip(), fim.strip() or None,
                        l["tipo"], l["descricao"]))
    n["quebra_serie"] = carga(
        "ref.quebra_serie", ["categoria", "data_inicio", "data_fim", "tipo", "descricao"],
        quebras)

    cat = Catalog.load(_caminho_catalogo(ler_regras(dir)["catalogo"], dir))
    linhas = [(e.codigo, e.tipo, e.grupo or "nucleo_pvd", e.natureza) for e in cat.entries]
    linhas += [(e.codigo, e.tipo, e.grupo, e.natureza) for e in cat.extensions]
    n["catalogo"] = carga("ref.catalogo", ["codigo", "tipo", "grupo", "natureza"], linhas)
    return n
