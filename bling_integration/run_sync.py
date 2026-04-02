"""
Ponto de entrada da sincronização de pedidos Bling.

Uso:
    # Importação completa (todo o histórico a partir de 2020-01-01)
    python run_sync.py --modo completo

    # Importação completa desde uma data específica
    python run_sync.py --modo completo --inicio 2023-01-01

    # Somente novos pedidos (padrão)
    python run_sync.py
    python run_sync.py --modo incremental

    # Apenas uma conta específica
    python run_sync.py --conta conta_1
"""

from __future__ import annotations
import argparse
import logging
import sys
from datetime import date

from auth import TokenManager
from client import BlingClient
from config import load_accounts
from db import Database
from sync import SyncManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sincronização de pedidos Bling para SQLite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--modo",
        choices=["completo", "incremental"],
        default="incremental",
        help="completo: importa todo o histórico | incremental: somente novos (padrão)",
    )
    parser.add_argument(
        "--inicio",
        type=date.fromisoformat,
        default=date(2020, 1, 1),
        metavar="AAAA-MM-DD",
        help="Data inicial para o modo completo (padrão: 2020-01-01)",
    )
    parser.add_argument(
        "--conta",
        default=None,
        metavar="NOME",
        help="Sincroniza apenas esta conta (ex: conta_1). Padrão: todas.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    accounts = load_accounts()

    if not accounts:
        logger.error(
            "Nenhuma conta configurada. Verifique o arquivo .env "
            "(veja .env.example para o formato)."
        )
        sys.exit(1)

    if args.conta:
        accounts = [a for a in accounts if a.name == args.conta]
        if not accounts:
            logger.error("Conta '%s' não encontrada no arquivo .env.", args.conta)
            sys.exit(1)

    db = Database()
    try:
        for account in accounts:
            logger.info("=" * 60)
            logger.info("Conta: %s", account.name)
            logger.info("=" * 60)

            token_manager = TokenManager(account)
            client = BlingClient(token_manager)
            sync = SyncManager(client, db, account.name)

            if args.modo == "completo":
                total = sync.sync_full_history(args.inicio)
            else:
                total = sync.sync_incremental()

            logger.info("Resumo [%s]: %d pedidos sincronizados", account.name, total)
            logger.info("Total no banco [%s]: %d registros", account.name, db.count(account.name))

    except KeyboardInterrupt:
        logger.warning("Sincronização interrompida pelo usuário.")
    except Exception:
        logger.exception("Erro inesperado durante a sincronização.")
        sys.exit(1)
    finally:
        db.close()

    logger.info("Sincronização concluída.")


if __name__ == "__main__":
    main()
