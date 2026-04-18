import requests
import responses as responses_lib

from okru.errors import OkTransportError
from okru.http import RetryPolicy, Transport


def test_retry_policy_delay_grows_exponentially():
    rp = RetryPolicy(backoff=1.0, jitter=0.0)
    assert rp.delay(0) == 1.0
    assert rp.delay(1) == 2.0
    assert rp.delay(2) == 4.0


def test_retry_policy_jitter_stays_in_range():
    rp = RetryPolicy(backoff=1.0, jitter=0.5)
    for _ in range(50):
        d = rp.delay(0)
        assert 0.5 <= d <= 1.5


def test_transport_success():
    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.GET, "https://x/y", json={"ok": True}, status=200)
        t = Transport(sleep=lambda _s: None)
        resp = t.request("GET", "https://x/y")
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}


def test_transport_retries_on_5xx_then_succeeds():
    sleeps: list[float] = []
    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.GET, "https://x/y", status=502)
        rsps.add(responses_lib.GET, "https://x/y", json={"ok": True}, status=200)
        t = Transport(
            retry=RetryPolicy(attempts=3, backoff=0.01, jitter=0.0),
            sleep=sleeps.append,
        )
        resp = t.request("GET", "https://x/y")
        assert resp.status_code == 200
        assert len(sleeps) == 1


def test_transport_retries_exhausted_returns_last_response():
    with responses_lib.RequestsMock() as rsps:
        rsps.add(responses_lib.GET, "https://x/y", status=503)
        rsps.add(responses_lib.GET, "https://x/y", status=503)
        t = Transport(
            retry=RetryPolicy(attempts=2, backoff=0.01, jitter=0.0),
            sleep=lambda _s: None,
        )
        resp = t.request("GET", "https://x/y")
        assert resp.status_code == 503


def test_transport_raises_on_repeated_connection_error():
    t = Transport(
        retry=RetryPolicy(attempts=2, backoff=0.001, jitter=0.0),
        sleep=lambda _s: None,
    )
    # URL, который гарантированно не ответит
    try:
        t.request("GET", "http://127.0.0.1:1/x")
    except OkTransportError:
        pass
    else:
        raise AssertionError("должна быть OkTransportError")


def test_transport_recovers_after_transient_connection_error(monkeypatch):
    """После одной сетевой ошибки должна успешно пройти попытка."""
    calls = {"n": 0}
    real_request = requests.Session.request

    def flaky(self, *args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise requests.ConnectionError("transient")
        return real_request(self, *args, **kwargs)

    monkeypatch.setattr(requests.Session, "request", flaky)
    with responses_lib.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add(responses_lib.GET, "https://x/y", json={"ok": 1}, status=200)
        t = Transport(
            retry=RetryPolicy(attempts=3, backoff=0.001, jitter=0.0),
            sleep=lambda _s: None,
        )
        resp = t.request("GET", "https://x/y")
        assert resp.status_code == 200
        assert calls["n"] == 2


def test_transport_context_manager_closes_session():
    with Transport() as t:
        assert t._session is not None
    # второе закрытие не должно падать
    t.close()
