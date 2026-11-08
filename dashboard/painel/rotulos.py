"""Rótulos em português para códigos das tabelas Gold."""
from __future__ import annotations

TIPO_PROCEDIMENTO = {
    "ACAO_PENAL": "Ação penal",
    "CARTA": "Carta precatória",
    "CAUTELAR_INCIDENTE": "Cautelar ou incidente",
    "EXECUCAO": "Execução",
    "INQUERITO": "Inquérito",
    "MPU": "Medida protetiva de urgência",
    "OUTROS": "Outros",
    "RECURSO": "Recurso",
}
CATEGORIA = {
    "AMEACA": "Ameaça",
    "DESCUMPRIMENTO_MPU": "Descumprimento de medida protetiva",
    "FEMINICIDIO": "Feminicídio",
    "FISICA": "Violência física",
    "MORAL": "Violência moral",
    "PATRIMONIAL": "Violência patrimonial",
    "PERSEGUICAO": "Perseguição",
    "PSICOLOGICA": "Violência psicológica",
    "SEXUAL": "Violência sexual",
    "VD_SEM_ESPECIFICACAO": "Violência doméstica sem especificação",
}
DESFECHO = {
    "CONDENACAO": "Condenação",
    "ABSOLVICAO": "Absolvição",
    "EXTINCAO_PUNIBILIDADE": "Extinção da punibilidade",
    "PRESCRICAO": "Prescrição",
    "OUTRO_ENCERRAMENTO": "Outro encerramento",
}
MARCO = {
    "decisao_mpu": "Decisão da MPU",
    "revogacao_mpu": "Revogação da MPU",
    "recebimento_denuncia": "Recebimento da denúncia",
    "sentenca": "Sentença",
}
SERIE = {"estrita": "Estrita", "ampliada": "Ampliada"}
MEDIDA_COBERTURA = {
    "mpu": "Medidas protetivas",
    "vd_sem_cartas": "Violência doméstica (sem cartas precatórias)",
    "feminicidio_acao_penal": "Feminicídio (ações penais)",
}


def rotulo_medida(bruto: str) -> str:
    t = bruto.replace("À  ", "à ").replace("Ã  ", "à ")
    if "(" in t and ")" not in t:
        t += "…)"
    return t[:1].upper() + t[1:]
