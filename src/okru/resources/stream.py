"""Методы группы ``stream``.

Документация: https://apiok.ru/dev/methods/rest/stream
"""

from __future__ import annotations

from collections.abc import Iterator

from okru.models import FeedItem
from okru.resources.base import Resource

DEFAULT_PATTERNS = "POST,PHOTO,FRIEND"


class StreamResource(Resource):
    def get(
        self,
        *,
        patterns: str = DEFAULT_PATTERNS,
        count: int = 20,
        anchor: str | None = None,
    ) -> tuple[list[FeedItem], str | None]:
        """``stream.get`` — одна страница ленты.

        Возвращает пару ``(items, next_anchor)``. Если ``next_anchor`` пуст —
        ленты больше нет.
        """
        payload = self._client.call(
            "stream.get",
            patterns=patterns,
            count=count,
            anchor=anchor,
        )
        entities = payload.get("feeds") or payload.get("entities") or []
        items = [FeedItem.from_dict(item) for item in entities]
        next_anchor = payload.get("anchor") or None
        return items, next_anchor

    def iter_feed(
        self,
        *,
        patterns: str = DEFAULT_PATTERNS,
        page_size: int = 20,
        max_items: int | None = None,
    ) -> Iterator[FeedItem]:
        """Итератор по ленте, автоматически листающий страницы.

        ``max_items`` — мягкий лимит: когда достигнут, итератор останавливается
        после выдачи последнего элемента.
        """
        anchor: str | None = None
        emitted = 0
        while True:
            items, anchor = self.get(patterns=patterns, count=page_size, anchor=anchor)
            for item in items:
                yield item
                emitted += 1
                if max_items is not None and emitted >= max_items:
                    return
            if not anchor or not items:
                return
