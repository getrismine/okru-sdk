# Contributing

## Что принимается

- Багфиксы (с тестом, воспроизводящим проблему).
- Новые методы API — по одной группе на PR.
- Документация и примеры — всегда рады.

## Локальный прогон

```bash
python -m venv .venv
.venv/Scripts/activate           # Linux/Mac: source .venv/bin/activate
pip install -e ".[dev]"

pytest                # тесты + покрытие
ruff check src tests  # линтер
```

Порог покрытия — 90%. Если он падает, PR не будет смёржен.

## Добавление нового метода API

1. Смотрим документацию на https://apiok.ru/dev/methods/
2. Определяемся: добавлять метод в существующий ресурс (`users`/`friends`/
   `group`/`stream`) или заводить новый (например, `photos`).
3. Если новый ресурс — создаём `src/okru/resources/<name>.py` с классом,
   унаследованным от `Resource`, и цепляем его в `Client` как
   `@cached_property`.
4. Метод ресурса — тонкая обёртка над `self._client.call("api.method", ...)`.
   Типизированные модели — через `Model.from_dict(data)`.
5. Тест — в `tests/test_resources.py` (там фикстура `responses` + `client`).
6. Коротко обновляем таблицу в `README.md` и `CHANGELOG.md`.

Пример минимального ресурса:

```python
# src/okru/resources/photos.py
from okru.resources.base import Resource

class PhotosResource(Resource):
    def get_photos(self, fid: str, count: int = 50) -> list[dict]:
        return self._client.call("photos.getPhotos", fid=fid, count=count)
```

## Стиль кода

- Форматирование: `ruff format` (настройки в `pyproject.toml`).
- Имена: snake_case для функций/переменных, CamelCase для классов.
- Русский в комментариях и docstring — ок (проект для русскоязычной
  аудитории), английский — тоже ок.
- Короткие функции. Если метод больше 50 строк — вероятно, можно
  разбить.

## Коммиты

Формат: `тип: краткое описание`. Пример: `feat: photos.getPhotos`,
`fix: подпись падает при пустом значении`.
