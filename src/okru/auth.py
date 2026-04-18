"""Помощники для OAuth2-авторизации в ok.ru.

Сам редирект пользователя делать не умеем — это задача веб-приложения.
SDK выдаёт корректный authorization URL и обменивает ``code`` на токен.

Документация: https://apiok.ru/ext/oauth/server
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

from okru.errors import OkAuthError
from okru.http import Transport

AUTHORIZE_URL = "https://connect.ok.ru/oauth/authorize"
TOKEN_URL = "https://api.ok.ru/oauth/token.do"


@dataclass(frozen=True)
class OAuthToken:
    """Токен, возвращаемый API после обмена или обновления."""

    access_token: str
    refresh_token: str | None
    token_type: str
    expires_in: int | None

    @classmethod
    def from_response(cls, payload: dict) -> OAuthToken:
        access = payload.get("access_token")
        if not access:
            raise OkAuthError(f"в ответе нет access_token: {payload!r}")
        return cls(
            access_token=str(access),
            refresh_token=payload.get("refresh_token"),
            token_type=str(payload.get("token_type", "session")),
            expires_in=payload.get("expires_in"),
        )


def authorization_url(
    *,
    client_id: str,
    redirect_uri: str,
    scope: list[str] | None = None,
    state: str | None = None,
    layout: str = "w",
) -> str:
    """Собрать URL для редиректа пользователя на страницу подтверждения доступа.

    ``scope`` — список прав (например ``["VALUABLE_ACCESS", "GET_EMAIL"]``).
    ``layout`` — ``w`` (десктоп), ``m`` (мобильный), ``a`` (для приложений).
    """
    if not client_id:
        raise OkAuthError("client_id пустой")
    if not redirect_uri:
        raise OkAuthError("redirect_uri пустой")

    query: dict[str, str] = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "layout": layout,
    }
    if scope:
        query["scope"] = ";".join(scope)
    if state:
        query["state"] = state
    return f"{AUTHORIZE_URL}?{urlencode(query)}"


class OAuthClient:
    """Обмен authorization code → token и refresh токенов."""

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        transport: Transport | None = None,
    ) -> None:
        if not all((client_id, client_secret, redirect_uri)):
            raise OkAuthError("client_id, client_secret и redirect_uri обязательны")
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._transport = transport or Transport()

    def exchange_code(self, code: str) -> OAuthToken:
        """Поменять authorization code на access/refresh-токен."""
        if not code:
            raise OkAuthError("code пустой")
        payload = self._post({
            "code": code,
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "redirect_uri": self._redirect_uri,
            "grant_type": "authorization_code",
        })
        return OAuthToken.from_response(payload)

    def refresh(self, refresh_token: str) -> OAuthToken:
        """Обновить истекший access_token по refresh_token."""
        if not refresh_token:
            raise OkAuthError("refresh_token пустой")
        payload = self._post({
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        })
        return OAuthToken.from_response(payload)

    def _post(self, data: dict) -> dict:
        resp = self._transport.request("POST", TOKEN_URL, data=data)
        if resp.status_code >= 400:
            raise OkAuthError(f"token endpoint вернул HTTP {resp.status_code}: {resp.text}")
        try:
            return resp.json()
        except ValueError as exc:
            raise OkAuthError(f"невалидный JSON от token endpoint: {resp.text}") from exc
