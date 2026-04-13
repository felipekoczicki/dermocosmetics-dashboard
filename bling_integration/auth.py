"""
Gerenciamento de tokens OAuth 2.0 do Bling.

Persiste access_token e refresh_token em tokens/<conta>.json.
Renova automaticamente o access_token quando expirado.
"""

from __future__ import annotations
import base64
import json
import logging
import time
from pathlib import Path

import requests

from config import BlingAccount

logger = logging.getLogger(__name__)

TOKEN_URL = "https://api.bling.com.br/Api/v3/oauth/token"
TOKEN_DIR = Path(__file__).parent / "tokens"
# Renova o token 60 segundos antes de expirar para evitar erros de borda
_EXPIRY_BUFFER_SECONDS = 60


class TokenManager:
    def __init__(self, account: BlingAccount):
        self.account = account
        self._token_file = TOKEN_DIR / f"{account.name}.json"
        self._tokens: dict = self._load_from_disk()

    # ------------------------------------------------------------------
    # Leitura / escrita em disco
    # ------------------------------------------------------------------

    def _load_from_disk(self) -> dict:
        if self._token_file.exists():
            try:
                return json.loads(self._token_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Não foi possível carregar tokens de %s: %s", self._token_file, exc)
        return {}

    def _save_to_disk(self, tokens: dict) -> None:
        TOKEN_DIR.mkdir(parents=True, exist_ok=True)
        self._token_file.write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")
        self._tokens = tokens
        logger.debug("Tokens salvos em %s", self._token_file)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def save_initial_tokens(self, access_token: str, refresh_token: str, expires_in: int = 3600) -> None:
        """Persiste os tokens obtidos no fluxo de autorização inicial."""
        self._save_to_disk({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": time.time() + expires_in - _EXPIRY_BUFFER_SECONDS,
        })

    def get_access_token(self) -> str:
        """Retorna um access_token válido, renovando-o se necessário."""
        if not self._tokens:
            raise RuntimeError(
                f"Nenhum token encontrado para '{self.account.name}'. "
                "Execute oauth_setup.py para autorizar esta conta."
            )
        if self._is_expired():
            logger.info("Token expirado para '%s'. Renovando...", self.account.name)
            self._refresh()
        return self._tokens["access_token"]

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _is_expired(self) -> bool:
        return time.time() >= self._tokens.get("expires_at", 0)

    def _basic_auth_header(self) -> str:
        raw = f"{self.account.client_id}:{self.account.client_secret}"
        return "Basic " + base64.b64encode(raw.encode()).decode()

    def _refresh(self) -> None:
        refresh_token = self._tokens.get("refresh_token")
        if not refresh_token:
            raise RuntimeError(
                f"Refresh token ausente para '{self.account.name}'. "
                "Execute oauth_setup.py novamente."
            )
        resp = requests.post(
            TOKEN_URL,
            headers={"Authorization": self._basic_auth_header()},
            data={"grant_type": "refresh_token", "refresh_token": refresh_token},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self._save_to_disk({
            "access_token": data["access_token"],
            # O Bling pode ou não rotacionar o refresh_token
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_at": time.time() + data.get("expires_in", 3600) - _EXPIRY_BUFFER_SECONDS,
        })
        logger.info("Token renovado com sucesso para '%s'.", self.account.name)
