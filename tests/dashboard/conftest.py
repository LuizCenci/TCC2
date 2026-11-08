import shutil
import sys
from pathlib import Path

import pytest

DASH = Path(__file__).resolve().parents[2] / "dashboard"
if str(DASH) not in sys.path:
    sys.path.insert(0, str(DASH))


@pytest.fixture
def pasta_copia(tmp_path) -> Path:
    from painel import config
    destino = tmp_path / "exportacao"
    shutil.copytree(config.PASTA_EXPORTACAO, destino)
    return destino
