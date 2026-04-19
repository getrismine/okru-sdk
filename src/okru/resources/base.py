"""Базовый класс для ресурсов API."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from okru.client import Client


class Resource:
    def __init__(self, client: Client) -> None:
        self._client = client
