"""Типизированные модели для популярных сущностей API.

Только поля, которые чаще всего нужны. Сырой ответ всегда доступен
в ``raw`` — если нужного поля нет в модели, его можно достать оттуда.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class User:
    uid: str
    first_name: str | None = None
    last_name: str | None = None
    birthday: str | None = None  # YYYY-MM-DD
    gender: str | None = None  # "male" | "female"
    locale: str | None = None
    age: int | None = None
    online: str | None = None  # "web", "mobile", "offline"
    pic_1: str | None = None  # 128px аватар
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @property
    def full_name(self) -> str:
        parts = [p for p in (self.first_name, self.last_name) if p]
        return " ".join(parts)

    @classmethod
    def from_dict(cls, data: dict) -> User:
        return cls(
            uid=str(data["uid"]),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            birthday=data.get("birthday"),
            gender=data.get("gender"),
            locale=data.get("locale"),
            age=data.get("age"),
            online=data.get("online"),
            pic_1=data.get("pic_1"),
            raw=dict(data),
        )


@dataclass
class Group:
    uid: str
    name: str
    description: str | None = None
    members_count: int | None = None
    pic_avatar: str | None = None
    shop_visible_admin: bool | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> Group:
        return cls(
            uid=str(data["uid"]),
            name=str(data.get("name", "")),
            description=data.get("description"),
            members_count=data.get("members_count"),
            pic_avatar=data.get("pic_avatar"),
            shop_visible_admin=data.get("shop_visible_admin"),
            raw=dict(data),
        )


@dataclass
class FeedItem:
    """Элемент ленты. Поля ``message`` и ``author_ref`` — для удобства."""

    id: str
    type: str
    date: str | None
    message: str | None
    author_ref: str | None  # "user:123" или "group:456"
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_dict(cls, data: dict) -> FeedItem:
        return cls(
            id=str(data.get("id", "")),
            type=str(data.get("type", "unknown")),
            date=data.get("date"),
            message=data.get("message"),
            author_ref=data.get("author_ref") or data.get("owner_ref"),
            raw=dict(data),
        )
