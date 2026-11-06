"""Arquivo de log rotativo para o pacote e para o orquestrador."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

FORMATO = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configurar_arquivo(caminho: Path, loggers: tuple[str, ...] = ("datajud_tcc",)) -> Path:
    """Anexa um handler de arquivo (UTF-8, rotativo) a cada logger. Idempotente."""
    absoluto = Path(caminho).resolve()
    absoluto.parent.mkdir(parents=True, exist_ok=True)
    for nome in loggers:
        logger = logging.getLogger(nome)
        if any(isinstance(h, RotatingFileHandler) and Path(h.baseFilename) == absoluto
               for h in logger.handlers):
            continue
        handler = RotatingFileHandler(absoluto, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(FORMATO))
        logger.addHandler(handler)
        if logger.level == logging.NOTSET or logger.level > logging.INFO:
            logger.setLevel(logging.INFO)
    return absoluto
