# okru-sdk

[![ci](https://github.com/getrismine/okru-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/getrismine/okru-sdk/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[English](README.md) | **Русский**

Python-клиент для [API ok.ru](https://apiok.ru/). OAuth2, подпись
запросов, типизированные модели, ретраи. Зависимость ровно одна — `requests`.

У ОК есть официальные SDK для Java/Android/iOS, но для Python нет
ничего вменяемого. Аналитики и скрипты автоматизации пишут обращения
к API руками через `requests`, каждый раз заново реализуя подпись и
обработку ошибок. Этот SDK закрывает пробел.

## Установка

```bash
pip install git+https://github.com/getrismine/okru-sdk.git
```

Требования: Python 3.10+. (Публикация на PyPI планируется; пока — установка из GitHub.)

## За 30 секунд

```python
from okru import Client

ok = Client(
    access_token="ВАШ_ACCESS_TOKEN",
    application_key="CBAPHLDJEB...",           # из настроек приложения
    application_secret_key="F5A0DE5D...",      # из настроек приложения
)

me = ok.users.get_current_user()
print(f"{me.full_name} ({me.uid})")

for uid in ok.friends.get():
    print(uid)
```

## OAuth2

```python
from okru import OAuthClient, authorization_url

# шаг 1 — куда редиректить пользователя
url = authorization_url(
    client_id="CBAPHLDJEB...",
    redirect_uri="https://my-app.example/cb",
    scope=["VALUABLE_ACCESS", "GET_EMAIL"],
    state="random-csrf-token",
)

# шаг 2 — обмен code на токен (в handler'е redirect_uri)
oauth = OAuthClient(
    client_id="CBAPHLDJEB...",
    client_secret="APP_SECRET",
    redirect_uri="https://my-app.example/cb",
)
token = oauth.exchange_code(code_from_query_string)

# шаг 3 — обновление, когда access_token истёк
new_token = oauth.refresh(token.refresh_token)
```

## Лента

`iter_feed` сам листает страницы по `anchor`:

```python
for item in ok.stream.iter_feed(patterns="POST,PHOTO", max_items=200):
    print(item.date, item.message)
```

## Реализованные методы

| Группа    | Методы API                                   |
|-----------|----------------------------------------------|
| users     | `getCurrentUser`, `getInfo`                  |
| friends   | `get`, `getMutualFriends`                    |
| group     | `getInfo`, `getMembers`                      |
| stream    | `get` (+ итератор `iter_feed`)               |

Покрыто не всё. Если нужен метод, которого нет — `Client.call`
работает с любым методом API напрямую, а расширить ресурсы
несложно (смотри `CONTRIBUTING.md`).

```python
ok.call("photos.getPhotos", fid="42", count=50)
```

## Ошибки

Коды ошибок API мапятся в типизированные исключения:

| Код   | Исключение                     |
|-------|--------------------------------|
| 100, 105, 454 | `OkParamError`         |
| 102   | `OkInvalidSessionError`        |
| 103   | `OkInvalidAccessTokenError`    |
| 104   | `OkPermissionDeniedError`      |
| 1002  | `OkRateLimitError`             |
| прочее| `OkApiError`                   |

Базовый класс — `OkError`, все перечисленные наследуются от него.

```python
from okru import OkInvalidAccessTokenError, OkRateLimitError

try:
    me = ok.users.get_current_user()
except OkInvalidAccessTokenError:
    token = oauth.refresh(refresh_token)
    # повторить запрос с новым токеном
except OkRateLimitError:
    time.sleep(10)
```

## Ретраи и таймаут

Транспорт сам повторяет запросы при сетевых сбоях и HTTP
5xx/429. Параметры настраиваемые:

```python
from okru import Client, RetryPolicy, Transport

transport = Transport(
    timeout=30.0,
    retry=RetryPolicy(attempts=5, backoff=1.0, jitter=0.25),
)
ok = Client(..., transport=transport)
```

Экспоненциальный backoff с джиттером — чтобы параллельные клиенты
не синхронизировались после общего сбоя.

## Как устроено

```
okru/
├── client.py        # Client: точка входа, сборка параметров, диспетчер
├── signing.py       # подпись MD5 (apiok.ru/ext/oauth/server)
├── auth.py          # OAuth2: authorization URL, exchange, refresh
├── http.py          # транспорт с ретраями
├── errors.py        # иерархия исключений
├── models.py        # User / Group / FeedItem
└── resources/       # обёртки над методами API
```

- `Client` знает про API, но не про HTTP — за HTTP отвечает `Transport`.
- Ресурсы (`users`, `friends`, `group`, `stream`) — тонкие фасады поверх
  `Client.call`. Тесты любой группы — это моки одного HTTP-вызова.
- Сырой ответ всегда доступен в поле `.raw` модели. Если нужного поля
  нет в dataclass, достаём из dict.

## Разработка

```bash
git clone https://github.com/getrismine/okru-sdk.git
cd okru-sdk
python -m venv .venv && .venv/Scripts/activate  # или source .venv/bin/activate
pip install -e ".[dev]"

pytest           # тесты + покрытие
ruff check .     # линтер
```

Минимальный порог покрытия — 90%. На момент релиза 0.1.0 — 99.7%.

## Что дальше

- `photos.*`, `video.*` — обёртки для медиа.
- Асинхронная версия клиента (httpx).
- Простой CLI: `okru user get 42` (аналог `gh`).
- Помощник пагинации для методов, где он не сделан.

PR-ы приветствуются. Правила — в [CONTRIBUTING.md](CONTRIBUTING.md).

## Авторы

Проект выполнен студентами группы Б1124-38.03.05 ба(1), ДВФУ:

- Шевцов Семён Валентинович — shevtcov.sva@dvfu.ru
- Гайнутдинов Роман Алексеевич — gainutdinov.ra@dvfu.ru

## Лицензия

MIT — делайте что угодно, только не забудьте про copyright notice.
