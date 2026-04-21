"""Минимальный пример: взять текущего пользователя и список друзей.

Запуск:
    OKRU_ACCESS_TOKEN=...   \
    OKRU_APP_KEY=...        \
    OKRU_APP_SECRET=...     \
    python docs/examples/quickstart.py
"""

from __future__ import annotations

import os
import sys

from okru import Client, OkError


def main() -> int:
    try:
        ok = Client(
            access_token=os.environ["OKRU_ACCESS_TOKEN"],
            application_key=os.environ["OKRU_APP_KEY"],
            application_secret_key=os.environ["OKRU_APP_SECRET"],
        )
    except KeyError as missing:
        print(f"не задана переменная окружения: {missing.args[0]}", file=sys.stderr)
        return 2

    try:
        me = ok.users.get_current_user()
        print(f"Вы: {me.full_name} (uid={me.uid})")

        friend_ids = ok.friends.get()
        print(f"Друзей: {len(friend_ids)}")

        if friend_ids:
            first5 = ok.users.get_info(friend_ids[:5])
            print("Первые 5:")
            for u in first5:
                print(f"  {u.uid}  {u.full_name}")
    except OkError as exc:
        print(f"ошибка API: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
