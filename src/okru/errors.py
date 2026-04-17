"""Исключения, соответствующие кодам ошибок API ok.ru.

Коды ошибок — по документации apiok.ru. Если сервер вернул неизвестный код,
поднимается базовый ``OkApiError`` с сырым телом.
"""

from __future__ import annotations

from dataclasses import dataclass


class OkError(Exception):
    """База для всех ошибок SDK."""


class OkTransportError(OkError):
    """Сетевой сбой: таймаут, DNS, разрыв соединения."""


class OkAuthError(OkError):
    """Проблемы авторизации на стороне SDK (нет токена, неверные параметры)."""


@dataclass
class OkApiError(OkError):
    """Ошибка, пришедшая из API (HTTP 2xx с полем ``error_code``).

    ``code`` — числовой код из ответа, ``message`` — текст ошибки,
    ``data`` — сырой JSON ответа (для отладки).
    """

    code: int
    message: str
    data: dict | None = None

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class OkInvalidSessionError(OkApiError):
    """102: сессия недействительна (нужен re-auth)."""


class OkInvalidAccessTokenError(OkApiError):
    """103: access_token недействителен."""


class OkPermissionDeniedError(OkApiError):
    """104: у приложения нет нужных прав."""


class OkRateLimitError(OkApiError):
    """1002: превышен лимит запросов, нужно подождать."""


class OkParamError(OkApiError):
    """100, 105, 454: ошибки в параметрах запроса."""


_CODE_MAP: dict[int, type[OkApiError]] = {
    100: OkParamError,
    102: OkInvalidSessionError,
    103: OkInvalidAccessTokenError,
    104: OkPermissionDeniedError,
    105: OkParamError,
    454: OkParamError,
    1002: OkRateLimitError,
}


def from_response(payload: dict) -> OkApiError:
    """Собрать типизированное исключение из JSON-ответа API."""
    code = int(payload.get("error_code", 0))
    message = str(payload.get("error_msg", "неизвестная ошибка"))
    cls = _CODE_MAP.get(code, OkApiError)
    return cls(code=code, message=message, data=payload)
