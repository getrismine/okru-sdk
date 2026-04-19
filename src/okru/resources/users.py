"""Методы группы ``users``.

Документация: https://apiok.ru/dev/methods/rest/users
"""

from __future__ import annotations

from okru.models import User
from okru.resources.base import Resource

DEFAULT_FIELDS = [
    "uid",
    "first_name",
    "last_name",
    "birthday",
    "gender",
    "locale",
    "age",
    "online",
    "pic_1",
]


class UsersResource(Resource):
    def get_current_user(self, fields: list[str] | None = None) -> User:
        """``users.getCurrentUser`` — профиль владельца текущего токена."""
        data = self._client.call(
            "users.getCurrentUser",
            fields=",".join(fields or DEFAULT_FIELDS),
        )
        return User.from_dict(data)

    def get_info(self, uids: list[str], fields: list[str] | None = None) -> list[User]:
        """``users.getInfo`` — пачка пользователей по их UID.

        Возвращает пользователей в порядке, в котором пришли ``uids``.
        """
        if not uids:
            return []
        data = self._client.call(
            "users.getInfo",
            uids=",".join(uids),
            fields=",".join(fields or DEFAULT_FIELDS),
        )
        return [User.from_dict(item) for item in data]
