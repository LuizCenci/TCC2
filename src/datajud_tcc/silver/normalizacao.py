"""Normalização pura (sem banco) de um hit da API Datajud para linhas da Silver."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RegistroNormalizado:
    registro: dict
    identificador: dict
    assuntos: list[dict]
    movimentos: list[dict]


def _iso(texto):
    """ISO 8601 (com 'Z') para datetime com fuso; None se ausente ou inválido."""
    if not texto:
        return None
    try:
        return datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        return None


def _data_ajuizamento(original):
    if not original:
        return None
    try:
        return datetime.strptime(str(original), "%Y%m%d%H%M%S")
    except ValueError:
        return None


def _int_ou_none(valor):
    if valor is None:
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def _orgao_movimento(mov):
    org = mov.get("orgaoJulgador") or {}
    original = org.get("codigo")
    original = None if original is None else str(original)
    codigo = int(original) if original is not None and re.fullmatch(r"\d+", original) else None
    return original, codigo, org.get("nome")


def _assuntos(lista):
    saida = []
    for item in lista or []:
        itens, aninhado = (item, True) if isinstance(item, list) else ([item], False)
        for a in itens:
            saida.append({
                "posicao": len(saida),
                "assunto_codigo": _int_ou_none(a.get("codigo")),
                "nome_original": a.get("nome"),
                "veio_aninhado": aninhado,
            })
    return saida


def _movimentos(lista, ajuizamento):
    movs = []
    for i, m in enumerate(lista or []):
        data_hora = _iso(m.get("dataHora"))
        dias = None
        if data_hora is not None and ajuizamento is not None:
            dias = (data_hora.replace(tzinfo=None) - ajuizamento).days
        original, codigo, nome = _orgao_movimento(m)
        movs.append({
            "codigo": _int_ou_none(m.get("codigo")),
            "nome_original": m.get("nome"),
            "data_hora": data_hora,
            "dias_desde_ajuizamento": dias,
            "orgao_codigo_original": original,
            "orgao_codigo": codigo,
            "orgao_nome": nome,
            "ordem_original": i,
            "ordem_cronologica": None,
            "complementos": [
                {"ordem": j, "codigo": c.get("codigo"), "descricao": c.get("descricao"),
                 "valor": c.get("valor"), "nome": c.get("nome")}
                for j, c in enumerate(m.get("complementosTabelados") or [])
            ],
        })
    ordenados = sorted(
        movs,
        key=lambda x: (x["data_hora"] is None,
                       x["data_hora"].timestamp() if x["data_hora"] else 0,
                       x["ordem_original"]),
    )
    for pos, m in enumerate(ordenados):
        m["ordem_cronologica"] = pos
    return movs


def _ano_cnj(numero):
    digitos = re.sub(r"\D", "", numero or "")
    return int(digitos[9:13]) if len(digitos) == 20 else None


def normalizar_hit(hit: dict, *, run_id: str, ano: int, pagina: int) -> RegistroNormalizado:
    src = hit.get("_source") or {}
    classe = src.get("classe") or {}
    orgao = src.get("orgaoJulgador") or {}
    sistema = src.get("sistema") or {}
    formato = src.get("formato") or {}
    original = src.get("dataAjuizamento")
    ajuizamento = _data_ajuizamento(original)
    movimentos = _movimentos(src.get("movimentos"), ajuizamento)
    registro = {
        "run_id": run_id,
        "api_id": hit.get("_id"),
        "ano_particao": ano,
        "pagina": pagina,
        "tribunal": src.get("tribunal"),
        "grau": src.get("grau"),
        "nivel_sigilo": src.get("nivelSigilo"),
        "classe_codigo": _int_ou_none(classe.get("codigo")),
        "classe_nome": classe.get("nome"),
        "orgao_codigo": _int_ou_none(orgao.get("codigo")),
        "orgao_nome": orgao.get("nome"),
        "municipio_sede_ibge": _int_ou_none(orgao.get("codigoMunicipioIBGE")),
        "data_ajuizamento_original": None if original is None else str(original),
        "data_ajuizamento": ajuizamento,
        "data_ultima_atualizacao": _iso(src.get("dataHoraUltimaAtualizacao")),
        "indexado_em": _iso(src.get("@timestamp")),
        "sistema_codigo": _int_ou_none(sistema.get("codigo")),
        "sistema_nome": sistema.get("nome"),
        "formato_codigo": _int_ou_none(formato.get("codigo")),
        "formato_nome": formato.get("nome"),
        "n_movimentos": len(movimentos),
        "hash_source": hashlib.sha256(
            json.dumps(src, sort_keys=True, ensure_ascii=False,
                       separators=(",", ":")).encode("utf-8")).hexdigest(),
    }
    numero = src.get("numeroProcesso")
    identificador = {
        "numero_processo": None if numero is None else str(numero),
        "id_source": src.get("id"),
        "ano_numero_cnj": _ano_cnj(numero),
    }
    return RegistroNormalizado(registro, identificador, _assuntos(src.get("assuntos")), movimentos)
