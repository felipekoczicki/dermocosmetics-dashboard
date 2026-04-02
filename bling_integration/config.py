"""
Carrega configurações das contas Bling a partir de variáveis de ambiente.

Arquivo .env esperado:
    BLING_CONTA1_CLIENT_ID=...
    BLING_CONTA1_CLIENT_SECRET=...
    BLING_CONTA2_CLIENT_ID=...
    BLING_CONTA2_CLIENT_SECRET=...
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


@dataclass(frozen=True)
class BlingAccount:
    name: str          # ex: "conta_1"
    client_id: str
    client_secret: str


def load_accounts() -> list[BlingAccount]:
    """Carrega todas as contas definidas nas variáveis BLING_CONTAn_*."""
    accounts: list[BlingAccount] = []
    for i in range(1, 20):
        client_id = os.getenv(f"BLING_CONTA{i}_CLIENT_ID", "").strip()
        if not client_id:
            break
        client_secret = os.getenv(f"BLING_CONTA{i}_CLIENT_SECRET", "").strip()
        if not client_secret:
            raise ValueError(
                f"BLING_CONTA{i}_CLIENT_ID definido mas BLING_CONTA{i}_CLIENT_SECRET está ausente."
            )
        accounts.append(BlingAccount(name=f"conta_{i}", client_id=client_id, client_secret=client_secret))
    return accounts
