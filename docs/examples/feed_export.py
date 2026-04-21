"""Экспортировать ленту пользователя в JSONL-файл.

Типовой use case: бэкап, аналитика, перенос данных. Скрипт листает
ленту с помощью ``stream.iter_feed`` и пишет каждую запись отдельной
строкой в JSON Lines (удобно читать pandas / jq).

Запуск:
    python docs/examples/feed_export.py --out feed.jsonl --limit 500
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from okru import Client, OkError


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Экспорт ленты в JSONL")
    p.add_argument("--out", type=Path, default=Path("feed.jsonl"),
                   help="файл назначения (по умолчанию feed.jsonl)")
    p.add_argument("--limit", type=int, default=None,
                   help="максимум записей (по умолчанию без лимита)")
    p.add_argument("--patterns", default="POST,PHOTO,FRIEND",
                   help="типы событий через запятую")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    try:
        ok = Client(
            access_token=os.environ["OKRU_ACCESS_TOKEN"],
            application_key=os.environ["OKRU_APP_KEY"],
            application_secret_key=os.environ["OKRU_APP_SECRET"],
        )
    except KeyError as missing:
        print(f"не задана переменная окружения: {missing.args[0]}", file=sys.stderr)
        return 2

    written = 0
    try:
        with args.out.open("w", encoding="utf-8") as fh:
            for item in ok.stream.iter_feed(patterns=args.patterns, max_items=args.limit):
                fh.write(json.dumps(item.raw, ensure_ascii=False))
                fh.write("\n")
                written += 1
                if written % 100 == 0:
                    print(f"  ...{written}", file=sys.stderr)
    except OkError as exc:
        print(f"ошибка API: {exc}", file=sys.stderr)
        return 1

    print(f"готово: {written} записей → {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
