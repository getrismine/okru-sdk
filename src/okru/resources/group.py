"""Методы группы ``group``.

Документация: https://apiok.ru/dev/methods/rest/group
"""

from __future__ import annotations

from okru.models import Group
from okru.resources.base import Resource

DEFAULT_FIELDS = [
    "uid",
    "name",
    "description",
    "members_count",
    "pic_avatar",
]


class GroupResource(Resource):
    def get_info(self, uids: list[str], fields: list[str] | None = None) -> list[Group]:
        """``group.getInfo`` — информация о группах по их UID."""
        if not uids:
            return []
        data = self._client.call(
            "group.getInfo",
            uids=",".join(uids),
            fields=",".join(fields or DEFAULT_FIELDS),
        )
        return [Group.from_dict(item) for item in data]

    def get_members(self, group_id: str, count: int = 100, anchor: str | None = None) -> dict:
        """``group.getMembers`` — список участников группы.

        Возвращает dict с ключами ``members`` (список UID) и ``anchor``
        (курсор для следующей страницы).
        """
        if not group_id:
            raise ValueError("group_id обязателен")
        return self._client.call(
            "group.getMembers",
            group_id=group_id,
            count=count,
            anchor=anchor,
        )
