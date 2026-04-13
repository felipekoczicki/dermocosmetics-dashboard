"""
Configuração inicial OAuth 2.0 para cada conta Bling.

Execute uma única vez por conta para obter o par access_token / refresh_token.
Após isso, o sistema renova os tokens automaticamente.

Uso:
    python oauth_setup.py
"""

from __future__ import annotations
import base64
import urllib.parse
import webbrowser

import requests

from auth import TokenManager
from config import BlingAccount, load_accounts

AUTH_URL = "https://api.bling.com.br/Api/v3/oauth/authorize"
TOKEN_URL = "https://api.bling.com.br/Api/v3/oauth/token"


def _basic_auth(client_id: str, client_secret: str) -> str:
    raw = f"{client_id}:{client_secret}"
    return "Basic " + base64.b64encode(raw.encode()).decode()


def setup_account(account: BlingAccount) -> None:
    print(f"\n{'='*60}")
    print(f"  Conta: {account.name}  (client_id: {account.client_id[:8]}...)")
    print(f"{'='*60}")

    # 1. Gera a URL de autorização
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": account.client_id,
        "state": account.name,
    })
    auth_url = f"{AUTH_URL}?{params}"

    print("\nPasso 1 — Acesse o link abaixo para autorizar a integração:")
    print(f"\n  {auth_url}\n")

    try:
        webbrowser.open(auth_url)
        print("  (O navegador foi aberto automaticamente)")
    except Exception:
        print("  (Copie e cole o link no navegador manualmente)")

    print(
        "\nPasso 2 — Após autorizar, o Bling redirecionará para uma URL com ?code=XXXXX\n"
        "          Copie apenas o valor do parâmetro 'code'."
    )
    code = input("\nCole o código de autorização aqui: ").strip()
    if not code:
        print("Código em branco. Pulando esta conta.")
        return

    # 2. Troca o código pelo par de tokens
    resp = requests.post(
        TOKEN_URL,
        headers={"Authorization": _basic_auth(account.client_id, account.client_secret)},
        data={"grant_type": "authorization_code", "code": code},
        timeout=30,
    )

    if not resp.ok:
        print(f"Erro ao obter tokens: {resp.status_code} — {resp.text}")
        return

    data = resp.json()
    manager = TokenManager(account)
    manager.save_initial_tokens(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=data.get("expires_in", 3600),
    )
    print(f"\nTokens salvos com sucesso em tokens/{account.name}.json")


def main() -> None:
    accounts = load_accounts()
    if not accounts:
        print(
            "Nenhuma conta encontrada.\n"
            "Certifique-se de que o arquivo .env está configurado corretamente.\n"
            "Consulte .env.example para o formato esperado."
        )
        return

    print(f"Encontradas {len(accounts)} conta(s) para configurar.")
    for account in accounts:
        setup_account(account)

    print("\nConfiguração concluída. Você já pode executar run_sync.py.")


if __name__ == "__main__":
    main()
