import logging

from datajud_tcc.registro_log import configurar_arquivo


def test_configurar_arquivo_grava_e_e_idempotente(tmp_path):
    alvo = tmp_path / "logs" / "x.log"
    logger = logging.getLogger("datajud_tcc")
    antes = list(logger.handlers)
    try:
        configurar_arquivo(alvo)
        configurar_arquivo(alvo)
        logging.getLogger("datajud_tcc.teste").info("página concluída: ação")
        for h in logger.handlers:
            h.flush()
        assert alvo.read_text(encoding="utf-8").count("página concluída: ação") == 1
    finally:
        for h in list(logger.handlers):
            if h not in antes:
                logger.removeHandler(h)
                h.close()
