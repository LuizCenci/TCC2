"""Leitura e validação das referências versionadas da Gold."""

import csv
from pathlib import Path

import yaml

DIR_PADRAO = Path("config/gold")

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
