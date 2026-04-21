# Changelog

Формат — [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/).
Версионирование — [SemVer](https://semver.org/lang/ru/).

## [Unreleased]

## [0.1.0] — 2026-04-20

Первый релиз.

### Добавлено
- `Client` — синхронный клиент API с автоматической подписью запросов.
- `OAuthClient` + `authorization_url` — хелперы для OAuth2-флоу.
- Ресурсы: `users`, `friends`, `group`, `stream`.
- Модели: `User`, `Group`, `FeedItem`.
- Иерархия исключений: `OkError` и производные под конкретные коды
  (`OkInvalidAccessTokenError`, `OkRateLimitError` и т.д.).
- `Transport` с ретраями (экспоненциальный backoff + jitter) для 5xx/429
  и сетевых ошибок.
- CI (GitHub Actions) на Python 3.10 / 3.11 / 3.12, Linux и Windows.
- Покрытие тестами 99.7%.

[Unreleased]: https://github.com/getrismine/okru-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/getrismine/okru-sdk/releases/tag/v0.1.0
