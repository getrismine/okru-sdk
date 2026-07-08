# okru-sdk

[![ci](https://github.com/getrismine/okru-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/getrismine/okru-sdk/actions/workflows/ci.yml)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**English** | [Русский](README.ru.md)

A Python client for the [ok.ru API](https://apiok.ru/) (Odnoklassniki — one of the largest Russian social networks). OAuth2, request signing, typed models, automatic retries. Exactly one dependency: `requests`.

OK ships official SDKs for Java/Android/iOS — but nothing sane exists for Python. Analysts and automation scripts end up hand-rolling `requests` calls, re-implementing the signature scheme and error handling every single time. This SDK closes that gap.

## Installation

```bash
pip install git+https://github.com/getrismine/okru-sdk.git
```

Requires Python 3.10+. (PyPI release is planned; until then install from GitHub.)

## 30 seconds to first call

```python
from okru import Client

ok = Client(
    access_token="YOUR_ACCESS_TOKEN",
    application_key="CBAPHLDJEB...",           # from your app settings
    application_secret_key="F5A0DE5D...",      # from your app settings
)

me = ok.users.get_current_user()
print(f"{me.full_name} ({me.uid})")

for uid in ok.friends.get():
    print(uid)
```

## OAuth2

```python
from okru import OAuthClient, authorization_url

# step 1 — where to redirect the user
url = authorization_url(
    client_id="CBAPHLDJEB...",
    redirect_uri="https://my-app.example/cb",
    scope=["VALUABLE_ACCESS", "GET_EMAIL"],
    state="random-csrf-token",
)

# step 2 — exchange the code for a token (in your redirect_uri handler)
oauth = OAuthClient(
    client_id="CBAPHLDJEB...",
    client_secret="APP_SECRET",
    redirect_uri="https://my-app.example/cb",
)
token = oauth.exchange_code(code_from_query_string)

# step 3 — refresh when the access_token expires
new_token = oauth.refresh(token.refresh_token)
```

## Feed

`iter_feed` handles `anchor`-based pagination for you:

```python
for item in ok.stream.iter_feed(patterns="POST,PHOTO", max_items=200):
    print(item.date, item.message)
```

## Implemented methods

| Group     | API methods                                   |
|-----------|-----------------------------------------------|
| users     | `getCurrentUser`, `getInfo`                   |
| friends   | `get`, `getMutualFriends`                     |
| group     | `getInfo`, `getMembers`                       |
| stream    | `get` (+ the `iter_feed` iterator)            |

Coverage is not complete. If a method you need is missing, `Client.call`
works with any API method directly, and adding resource wrappers is
easy (see `CONTRIBUTING.md`).

```python
ok.call("photos.getPhotos", fid="42", count=50)
```

## Errors

API error codes map to typed exceptions:

| Code  | Exception                      |
|-------|--------------------------------|
| 100, 105, 454 | `OkParamError`         |
| 102   | `OkInvalidSessionError`        |
| 103   | `OkInvalidAccessTokenError`    |
| 104   | `OkPermissionDeniedError`      |
| 1002  | `OkRateLimitError`             |
| other | `OkApiError`                   |

The base class is `OkError`; everything above inherits from it.

```python
from okru import OkInvalidAccessTokenError, OkRateLimitError

try:
    me = ok.users.get_current_user()
except OkInvalidAccessTokenError:
    token = oauth.refresh(refresh_token)
    # retry with the new token
except OkRateLimitError:
    time.sleep(10)
```

## Retries and timeouts

The transport retries on network failures and HTTP 5xx/429 out of the box. Everything is configurable:

```python
from okru import Client, RetryPolicy, Transport

transport = Transport(
    timeout=30.0,
    retry=RetryPolicy(attempts=5, backoff=1.0, jitter=0.25),
)
ok = Client(..., transport=transport)
```

Exponential backoff with jitter — so parallel clients don't synchronize after a shared outage.

## Architecture

```
okru/
├── client.py        # Client: entry point, parameter assembly, dispatch
├── signing.py       # MD5 request signing (apiok.ru/ext/oauth/server)
├── auth.py          # OAuth2: authorization URL, exchange, refresh
├── http.py          # transport with retries
├── errors.py        # exception hierarchy
├── models.py        # User / Group / FeedItem
└── resources/       # wrappers over API methods
```

- `Client` knows the API but not HTTP — HTTP is `Transport`'s job.
- Resources (`users`, `friends`, `group`, `stream`) are thin facades over
  `Client.call`. Testing any group means mocking a single HTTP call.
- The raw response is always available via the model's `.raw` field. If a
  field is missing from the dataclass, grab it from the dict.

## Development

```bash
git clone https://github.com/getrismine/okru-sdk.git
cd okru-sdk
python -m venv .venv && .venv/Scripts/activate  # or source .venv/bin/activate
pip install -e ".[dev]"

pytest           # tests + coverage
ruff check .     # linter
```

Minimum coverage bar is 90%. At the 0.1.0 release it was 99.7%.

## Roadmap

- `photos.*`, `video.*` — media wrappers.
- Async client (httpx).
- A simple CLI: `okru user get 42` (think `gh`).
- Pagination helper for methods that lack one.

PRs are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Authors

Built by students of group Б1124-38.03.05 ба(1), FEFU (Far Eastern Federal University):

- Semyon Shevtsov — shevtcov.sva@dvfu.ru
- Roman Gainutdinov — gainutdinov.ra@dvfu.ru

## License

MIT — do whatever you want, just keep the copyright notice.
