import pytest
import responses as responses_lib

from okru import Client
from okru.client import API_BASE
from okru.errors import (
    OkApiError,
    OkAuthError,
    OkInvalidAccessTokenError,
    OkRateLimitError,
)


def _mock_ok(responses, *, method, payload=None, status=200, body=None):
    """Добавить моковый ответ от API с валидной сигнатурой в query."""
    if body is not None:
        responses.add(responses_lib.GET, API_BASE, body=body, status=status)
    else:
        responses.add(responses_lib.GET, API_BASE, json=payload or {}, status=status)


def test_client_rejects_missing_credentials():
    with pytest.raises(OkAuthError):
        Client(access_token="", application_key="k", application_secret_key="s")
    with pytest.raises(OkAuthError):
        Client(access_token="t", application_key="", application_secret_key="s")
    with pytest.raises(OkAuthError):
        Client(access_token="t", application_key="k", application_secret_key="")


def test_client_call_adds_required_params(client, responses):
    _mock_ok(responses, method="users.getCurrentUser", payload={"uid": "1"})
    client.call("users.getCurrentUser", fields="uid")

    req = responses.calls[0].request
    # В query-строке должны быть служебные параметры
    assert "method=users.getCurrentUser" in req.url
    assert "application_key=APPKEY" in req.url
    assert "format=json" in req.url
    assert "sig=" in req.url
    assert "access_token=tok" in req.url


def test_client_call_rejects_empty_method(client):
    with pytest.raises(ValueError):
        client.call("")


def test_client_call_returns_parsed_json(client, responses):
    _mock_ok(responses, method="x", payload=[1, 2, 3])
    assert client.call("x") == [1, 2, 3]


def test_client_raises_mapped_api_error(client, responses):
    _mock_ok(responses, method="x", payload={"error_code": 103, "error_msg": "token bad"})
    with pytest.raises(OkInvalidAccessTokenError):
        client.call("x")


def test_client_raises_rate_limit_error(client, responses):
    _mock_ok(responses, method="x", payload={"error_code": 1002, "error_msg": "slow down"})
    with pytest.raises(OkRateLimitError):
        client.call("x")


def test_client_raises_on_http_error(client, responses):
    _mock_ok(responses, method="x", status=400, body="bad request")
    with pytest.raises(OkApiError) as exc:
        client.call("x")
    assert exc.value.code == 400


def test_client_raises_on_invalid_json(client, responses):
    _mock_ok(responses, method="x", body="not json")
    with pytest.raises(OkApiError):
        client.call("x")


def test_client_context_manager(client, responses):
    _mock_ok(responses, method="x", payload={})
    with client:
        client.call("x")


def test_client_signature_is_consistent(responses):
    """Повторный вызов с теми же параметрами должен давать ту же подпись."""
    _mock_ok(responses, method="x", payload={})
    _mock_ok(responses, method="x", payload={})
    c = Client(access_token="t", application_key="k", application_secret_key="s")
    c.call("users.get", uid="42")
    c.call("users.get", uid="42")
    sig1 = dict(q.split("=", 1) for q in responses.calls[0].request.url.split("?")[1].split("&"))["sig"]
    sig2 = dict(q.split("=", 1) for q in responses.calls[1].request.url.split("?")[1].split("&"))["sig"]
    assert sig1 == sig2


def test_client_drops_none_params(client, responses):
    _mock_ok(responses, method="x", payload={})
    client.call("users.get", uid="1", anchor=None)
    assert "anchor=" not in responses.calls[0].request.url
