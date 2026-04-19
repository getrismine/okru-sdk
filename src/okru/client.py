"""Основной клиент API.

Пример:

    from okru import Client

    ok = Client(
        access_token="...",
        application_key="CBAPHLDJEB...",
        application_secret_key="F5A0DE5...",
    )
    me = ok.users.get_current_user()
    print(me.full_name)
"""

from __future__ import annotations

from functools import cached_property
from typing import Any

from okru import signing
from okru.errors import OkApiError, OkAuthError, from_response
from okru.http import Transport

API_BASE = "https://api.ok.ru/fb.do"


class Client:
    """Синхронный клиент API ok.ru.

    ``application_secret_key`` обязателен для вычисления подписи запроса.
    ``application_key`` идёт параметром в каждом вызове (в OK он виден
    в настройках приложения).
    """

    def __init__(
        self,
        *,
        access_token: str,
        application_key: str,
        application_secret_key: str,
        base_url: str = API_BASE,
        transport: Transport | None = None,
    ) -> None:
        if not access_token:
            raise OkAuthError("access_token обязателен")
        if not application_key:
            raise OkAuthError("application_key обязателен")
        if not application_secret_key:
            raise OkAuthError("application_secret_key обязателен")

        self._access_token = access_token
        self._application_key = application_key
        self._session_secret = signing.session_secret(access_token, application_secret_key)
        self._base_url = base_url
        self._transport = transport or Transport()

    # -- transport -----------------------------------------------------------

    def call(self, method: str, **params: Any) -> Any:
        """Вызвать метод API. Возвращает распарсенный JSON (обычно dict).

        Подпись и служебные параметры (``access_token``, ``application_key``,
        ``format``, ``method``) добавляются автоматически.
        """
        if not method:
            raise ValueError("method не может быть пустым")

        signed = self._build_params(method, params)
        resp = self._transport.request("GET", self._base_url, params=signed)

        if resp.status_code >= 400:
            raise OkApiError(
                code=resp.status_code,
                message=f"HTTP {resp.status_code}",
                data={"body": resp.text[:500]},
            )

        try:
            payload = resp.json()
        except ValueError as exc:
            raise OkApiError(code=0, message="невалидный JSON в ответе") from exc

        if isinstance(payload, dict) and "error_code" in payload:
            raise from_response(payload)

        return payload

    def _build_params(self, method: str, params: dict) -> dict:
        cleaned = {k: v for k, v in params.items() if v is not None}
        cleaned.update({
            "method": method,
            "application_key": self._application_key,
            "format": "json",
        })
        cleaned["sig"] = signing.sign(cleaned, self._session_secret)
        cleaned["access_token"] = self._access_token
        return cleaned

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # -- resources -----------------------------------------------------------

    @cached_property
    def users(self):  # noqa: ANN201 — циклический импорт иначе
        from okru.resources.users import UsersResource
        return UsersResource(self)

    @cached_property
    def friends(self):  # noqa: ANN201
        from okru.resources.friends import FriendsResource
        return FriendsResource(self)

    @cached_property
    def group(self):  # noqa: ANN201
        from okru.resources.group import GroupResource
        return GroupResource(self)

    @cached_property
    def stream(self):  # noqa: ANN201
        from okru.resources.stream import StreamResource
        return StreamResource(self)
