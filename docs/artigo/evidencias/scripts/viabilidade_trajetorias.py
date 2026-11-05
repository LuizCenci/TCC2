# Viabilidade de trajetórias e de "resultado" a partir de códigos de movimento (2019-2025). Sem identificadores.
# Uso: python -I viabilidade_trajetorias.py <extrato.jsonl.gz> <saida.json>
import gzip, json, statistics, sys
from collections import Counter, defaultdict
PRINC = {279, 283, 10943, 10944, 282, 278, 288, 272}
# Desfechos por código TPU (hierarquia SGT: Magistrado > Julgamento; Decisão > Rejeição/Determinação).
DESFECHO = {
 219: "condenacao", 221: "condenacao_parcial",
 220: "absolvicao", 11876: "absolvicao_sumaria", 11877: "absolvicao_sumaria",
 11878: "extincao_prescricao", 11879: "extincao_decadencia_perempcao", 1046: "extincao_renuncia_perdao",
 1047: "extincao_retratacao", 1042: "extincao_morte_agente", 11411: "extincao_cumprimento_sursis",
 12735: "extincao_cumprimento_anpp", 1043: "extincao_outras", 1044: "extincao_outras", 1049: "extincao_outras",
 455: "sem_merito", 459: "sem_merito", 460: "sem_merito", 461: "sem_merito", 463: "sem_merito", 471: "sem_merito",
 402: "denuncia_rejeitada", 1063: "arquivamento_investigacao", 12430: "arquivamento_determinado",
}
# Eventos semânticos para trajetórias (canal "fase" e canal "cautelar").
EVENTO = {26: "distribuicao", 36: "redistribuicao", 391: "denuncia_recebida", 402: "denuncia_rejeitada",
          12750: "audiencia_instrucao_julgamento", 12749: "audiencia_instrucao", 12742: "audiencia_custodia",
          10953: "pronuncia", 848: "transito_julgado", 246: "arquivamento_definitivo", 849: "reativacao", 893: "desarquivamento",
          175: "prisao_flagrante", 12140: "flagrante_em_preventiva", 15032: "manutencao_preventiva", 818: "liberdade_provisoria",
          11423: "mpu_concedida", 11424: "mpu_concedida_parte", 11425: "mpu_negada", 11426: "mpu_revogada", 14733: "mpu_prorrogada"}
EVENTO.update({c: "julgamento:" + d for c, d in DESFECHO.items() if c not in EVENTO})
prim = Counter(); por_ano = defaultdict(Counter); n_ev = []; n_dist = []; variantes = Counter(); n = 0; tempo = defaultdict(list); com_assunto = defaultdict(Counter)
for line in gzip.open(sys.argv[1], "rt", encoding="utf-8"):
    r = json.loads(line)
    if r["classe"] not in PRINC: continue
    n += 1; movs = [(c, d) for c, d in r["movs"] if d is not None and d >= 0]
    d1 = next(((DESFECHO[c], d) for c, d in movs if c in DESFECHO), None)
    k = d1[0] if d1 else "sem_desfecho_observado"
    prim[k] += 1; por_ano[r["ano"]][k] += 1
    if d1: tempo[k].append(d1[1])
    a = set(r["assuntos"])
    cat = "feminicidio" if 12091 in a else "lesao" if a & {12194, 14943, 12196, 14945, 5560, 9647} else "descumprimento_mpu" if a & {14227, 14229} else "psicologica" if a & {14942, 14944} else "outros"
    com_assunto[cat][k] += 1
    ev = [EVENTO[c] for c, _ in movs if c in EVENTO]
    n_ev.append(len(ev)); n_dist.append(len(set(ev)))
    seq = []
    for e in ev:
        if not seq or seq[-1] != e: seq.append(e)
    variantes[" > ".join(seq[:8])] += 1
out = {"procedimentos_principais": n, "primeiro_desfecho": dict(prim.most_common()),
       "primeiro_desfecho_por_ano": {str(k): dict(v) for k, v in sorted(por_ano.items())},
       "primeiro_desfecho_por_categoria": {k: dict(v.most_common()) for k, v in com_assunto.items()},
       "dias_ate_desfecho_mediana": {k: statistics.median(v) for k, v in tempo.items()},
       "eventos_semanticos_por_processo": {"mediana": statistics.median(n_ev), "distintos_mediana": statistics.median(n_dist)},
       "variantes_distintas_8_primeiros": len(variantes), "variantes_top": variantes.most_common(12)}
json.dump(out, open(sys.argv[2], "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
