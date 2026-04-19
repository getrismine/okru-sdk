"""Методы группы ``friends``.

Документация: https://apiok.ru/dev/methods/rest/friends
"""

from __future__ import annotations

from okru.resources.base import Resource


class FriendsResource(Resource):
    def get(self, fid: str | None = None) -> list[str]:
        """``friends.get`` — список UID друзей.

        Если ``fid`` не указан, возвращает друзей текущего пользователя.
        """
        data = self._client.call("friends.get", fid=fid)
        # API возвращает либо список строк, либо список объектов с ключом uid
        return [str(x) if not isinstance(x, dict) else str(x["uid"]) for x in data]

    def get_mutual(self, target_id: str) -> list[str]:
        """``friends.getMutualFriends`` — общие друзья с ``target_id``."""
        if not target_id:
            raise ValueError("target_id обязателен")
        data = self._client.call("friends.getMutualFriends", target_id=target_id)
        return [str(x) for x in data]
