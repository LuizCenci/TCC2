"""Caminhos e constantes do painel."""
from pathlib import Path

RAIZ: Path = Path(__file__).resolve().parent.parent
RAIZ_REPO: Path = RAIZ.parent
PASTA_EXPORTACAO: Path = RAIZ_REPO / "outputs" / "publicacao" / "2026-11-05_gold-2026-11-11"
ARQUIVO_MESORREGIOES: Path = RAIZ / "dados" / "mesorregioes_pr.geojson"
