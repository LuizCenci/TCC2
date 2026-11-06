"""Command-line entry point for collection and reporting."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .catalog import Catalog
from .client import DatajudClient, DatajudError
from .collector import Collector
from .config import CollectionConfig
from .report import build_pilot_summary, write_markdown


CATALOG_PATH = Path("config/catalogs/tjpr_vcm_2026-10-18.yaml")


def _load_dotenv(path: Path = Path(".env"), chave: str = "DATAJUD_API_KEY") -> None:
    """Carrega `chave` (padrão DATAJUD_API_KEY) de um .env sem sobrescrever o ambiente."""
    if os.getenv(chave, "").strip() or not path.is_file():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, value = line.partition("=")
        if separator and key.strip() == chave:
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            os.environ.setdefault(chave, value)
            return


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="datajud-tcc")
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect", help="coletar páginas Bronze")
    collect.add_argument("--config", required=True, type=Path)
    collect.add_argument("--query-kind", choices=("main", "diagnostic"), default="main")
    collect.add_argument("--run-id")
    collect.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    report = subparsers.add_parser("report", help="gerar relatório agregado")
    report.add_argument("--run-root", required=True, type=Path)
    report.add_argument("--output", type=Path)
    report.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    subparsers.add_parser("silver-esquema", help="aplicar o esquema da Silver")
    silver_carregar = subparsers.add_parser(
        "silver-carregar", help="carregar uma execução Bronze na Silver"
    )
    silver_carregar.add_argument("--run-root", required=True, type=Path)
    subparsers.add_parser(
        "silver-marca-dagua", help="imprimir a maior data de atualização da Silver"
    )
    return parser


def _collect(args: argparse.Namespace) -> int:
    _load_dotenv()
    api_key = os.getenv("DATAJUD_API_KEY", "")
    if not api_key.strip():
        print("DATAJUD_API_KEY não foi informado no ambiente.", file=sys.stderr)
        return 2
    try:
        config = CollectionConfig.from_yaml(args.config)
        catalog = Catalog.load(args.catalog)
        client = DatajudClient(
            endpoint=config.endpoint,
            api_key=api_key,
            connect_timeout_seconds=config.connect_timeout_seconds,
            read_timeout_seconds=config.read_timeout_seconds,
            max_attempts=config.max_attempts,
            max_wait_seconds=config.max_wait_seconds,
        )
        run_id = args.run_id or (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
        )
        manifest = Collector(config, catalog, client).collect(run_id, args.query_kind)
    except (OSError, ValueError, DatajudError) as exc:
        print(f"coleta não iniciada/concluída: {exc}", file=sys.stderr)
        return 3
    print(f"run_id={manifest['run_id']} status={manifest['status']}")
    return 3 if manifest["status"] == "failed" else 0


def _report(args: argparse.Namespace) -> int:
    try:
        catalog = Catalog.load(args.catalog)
        summary = build_pilot_summary(args.run_root, catalog)
        destination = args.output or Path("outputs/pilot") / f"{args.run_root.name}.md"
        write_markdown(summary, destination)
    except (OSError, ValueError) as exc:
        print(f"relatório não gerado: {exc}", file=sys.stderr)
        return 3
    print(f"report={destination}")
    return 0


def _silver_esquema(args: argparse.Namespace) -> int:
    from .silver import conexao, esquema

    try:
        conn = conexao.conectar()
    except Exception:  # a mensagem pode conter o DSN; não exibir
        print("não foi possível conectar ao banco (verifique DATABASE_URL).", file=sys.stderr)
        return 3
    try:
        esquema.aplicar_esquema(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        print("esquema da Silver não aplicado.", file=sys.stderr)
        return 3
    finally:
        conn.close()
    print("esquema aplicado")
    return 0


def _silver_carregar(args: argparse.Namespace) -> int:
    from .registro_log import configurar_arquivo
    from .silver import carga, conexao, esquema

    configurar_arquivo(Path("work/logs/silver.log"))
    try:
        conn = conexao.conectar()
    except Exception:  # a mensagem pode conter o DSN; não exibir
        print("não foi possível conectar ao banco (verifique DATABASE_URL).", file=sys.stderr)
        return 3
    try:
        esquema.aplicar_esquema(conn)
        contagens = carga.carregar_execucao(conn, args.run_root)
        conn.commit()
    except carga.ExecucaoInvalida as exc:
        conn.rollback()
        print(f"execução inválida: {exc}", file=sys.stderr)
        return 3
    except Exception:
        conn.rollback()
        print("carga na Silver não concluída (erro inesperado).", file=sys.stderr)
        return 3
    finally:
        conn.close()
    print(" ".join(f"{chave}={valor}" for chave, valor in contagens.items()))
    return 0


def _silver_marca_dagua(args: argparse.Namespace) -> int:
    from .silver import conexao, esquema

    try:
        conn = conexao.conectar()
    except Exception:  # a mensagem pode conter o DSN; não exibir
        print("não foi possível conectar ao banco (verifique DATABASE_URL).", file=sys.stderr)
        return 3
    try:
        esquema.aplicar_esquema(conn)
        conn.commit()
        marca = conn.execute("SELECT max(data_ultima_atualizacao) FROM silver.registro").fetchone()[0]
    except Exception:
        conn.rollback()
        print("marca d'água não obtida (erro inesperado).", file=sys.stderr)
        return 3
    finally:
        conn.close()
    if marca is None:
        print("Silver sem registros com data de atualização: marca d'água indisponível.", file=sys.stderr)
        return 3
    marca = marca.astimezone(timezone.utc)
    print(marca.strftime("%Y-%m-%dT%H:%M:%S.") + f"{marca.microsecond // 1000:03d}Z")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )
    if args.command == "collect":
        return _collect(args)
    if args.command == "report":
        return _report(args)
    if args.command == "silver-esquema":
        return _silver_esquema(args)
    if args.command == "silver-carregar":
        return _silver_carregar(args)
    if args.command == "silver-marca-dagua":
        return _silver_marca_dagua(args)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
