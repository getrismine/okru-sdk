"""Тонкая обёртка над ``requests`` с ретраями и таймаутом.

Транспорт сам по себе ничего не знает про API ok.ru — он работает
с произвольными URL. Логика подписи и эндпоинтов живёт в :mod:`okru.client`.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any

import requests
from requests import Response, Session

from okru.errors import OkTransportError

DEFAULT_TIMEOUT = 15.0
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 0.5
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})


@dataclass(frozen=True)
class RetryPolicy:
    """Параметры ретраев. ``backoff`` — базовая задержка, растёт экспоненциально."""

    attempts: int = DEFAULT_RETRIES
    backoff: float = DEFAULT_BACKOFF
    jitter: float = 0.25

    def delay(self, attempt: int) -> float:
        """Задержка перед попыткой ``attempt`` (0-индексированная)."""
        base = self.backoff * (2**attempt)
        # ± jitter, чтобы параллельные клиенты не синхронизировались
        spread = base * self.jitter
        return base + random.uniform(-spread, spread)


class Transport:
    """Синхронный HTTP-транспорт.

    По умолчанию создаёт свой ``requests.Session``. Можно передать готовую,
    если нужно переиспользовать connection pool или настроить адаптер.
    """

    def __init__(
        self,
        *,
        session: Session | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry: RetryPolicy | None = None,
        sleep: Any = time.sleep,
    ) -> None:
        self._session = session or requests.Session()
        self._timeout = timeout
        self._retry = retry or RetryPolicy()
        self._sleep = sleep

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Response:
        last_exc: Exception | None = None
        for attempt in range(self._retry.attempts):
            try:
                resp = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    headers=headers,
                    timeout=self._timeout,
                )
            except requests.RequestException as exc:
                last_exc = exc
                if attempt == self._retry.attempts - 1:
                    raise OkTransportError(str(exc)) from exc
                self._sleep(self._retry.delay(attempt))
                continue

            if resp.status_code in RETRY_STATUS and attempt < self._retry.attempts - 1:
                self._sleep(self._retry.delay(attempt))
                continue

            return resp

        # сюда попадаем только если все попытки сорвались по исключению
        raise OkTransportError(str(last_exc) if last_exc else "нет успешного ответа")

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> Transport:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()
