"""Подпись запросов к API ok.ru.

Алгоритм (см. https://apiok.ru/ext/oauth/server):

1. Все параметры, кроме ``access_token`` и ``sig``, сортируются по ключу.
2. Конкатенируются как ``key=value`` без разделителей.
3. Для OAuth-токена секрет сессии = md5(access_token + application_secret_key).
4. sig = md5(params_string + session_secret).

Все MD5 возвращаются в lowercase hex.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping

EXCLUDED_FROM_SIG = frozenset({"access_token", "sig"})


def _md5_hex(data: str) -> str:
    return hashlib.md5(data.encode("utf-8")).hexdigest()


def session_secret(access_token: str, application_secret_key: str) -> str:
    """Секрет сессии, производный от токена и секрета приложения."""
    if not access_token:
        raise ValueError("access_token пустой")
    if not application_secret_key:
        raise ValueError("application_secret_key пустой")
    return _md5_hex(access_token + application_secret_key)


def build_params_string(params: Mapping[str, object]) -> str:
    """Сортированная строка параметров для подписи.

    ``access_token`` и ``sig`` игнорируются.
    Значения приводятся к строке как в URL (bool → ``true``/``false``, list → CSV).
    """
    parts = []
    for key in sorted(params):
        if key in EXCLUDED_FROM_SIG:
            continue
        value = params[key]
        if value is None:
            continue
        parts.append(f"{key}={_stringify(value)}")
    return "".join(parts)


def _stringify(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ",".join(_stringify(v) for v in value)
    return str(value)


def sign(params: Mapping[str, object], session_secret_key: str) -> str:
    """Посчитать значение ``sig`` для запроса."""
    if not session_secret_key:
        raise ValueError("session_secret_key пустой")
    return _md5_hex(build_params_string(params) + session_secret_key)
