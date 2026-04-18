import pytest
import responses as responses_lib

from okru import OAuthClient, OAuthToken, authorization_url
from okru.auth import AUTHORIZE_URL, TOKEN_URL
from okru.errors import OkAuthError


def test_authorization_url_minimal():
    url = authorization_url(client_id="app1", redirect_uri="https://x/cb")
    assert url.startswith(AUTHORIZE_URL + "?")
    assert "client_id=app1" in url
    assert "response_type=code" in url
    assert "redirect_uri=https%3A%2F%2Fx%2Fcb" in url


def test_authorization_url_with_scope_and_state():
    url = authorization_url(
        client_id="app1",
        redirect_uri="https://x/cb",
        scope=["VALUABLE_ACCESS", "GET_EMAIL"],
        state="s1",
    )
    assert "scope=VALUABLE_ACCESS%3BGET_EMAIL" in url
    assert "state=s1" in url


def test_authorization_url_rejects_empty_args():
    with pytest.raises(OkAuthError):
        authorization_url(client_id="", redirect_uri="https://x")
    with pytest.raises(OkAuthError):
        authorization_url(client_id="app", redirect_uri="")


def test_oauth_client_exchange_code(responses):
    responses.add(
        responses_lib.POST,
        TOKEN_URL,
        json={
            "access_token": "AT",
            "refresh_token": "RT",
            "token_type": "session",
            "expires_in": 1800,
        },
        status=200,
    )
    oc = OAuthClient(
        client_id="app",
        client_secret="s",
        redirect_uri="https://x/cb",
    )
    token = oc.exchange_code("CODE")
    assert isinstance(token, OAuthToken)
    assert token.access_token == "AT"
    assert token.refresh_token == "RT"
    assert token.expires_in == 1800


def test_oauth_client_refresh(responses):
    responses.add(
        responses_lib.POST,
        TOKEN_URL,
        json={"access_token": "AT2", "token_type": "session"},
        status=200,
    )
    oc = OAuthClient(client_id="a", client_secret="s", redirect_uri="https://x/cb")
    token = oc.refresh("RT")
    assert token.access_token == "AT2"
    assert token.refresh_token is None


def test_oauth_client_http_error(responses):
    responses.add(responses_lib.POST, TOKEN_URL, status=500, body="oops")
    oc = OAuthClient(client_id="a", client_secret="s", redirect_uri="https://x/cb")
    with pytest.raises(OkAuthError) as exc_info:
        oc.exchange_code("CODE")
    assert "500" in str(exc_info.value)


def test_oauth_client_invalid_json(responses):
    responses.add(responses_lib.POST, TOKEN_URL, body="not-json", status=200)
    oc = OAuthClient(client_id="a", client_secret="s", redirect_uri="https://x/cb")
    with pytest.raises(OkAuthError):
        oc.exchange_code("CODE")


def test_oauth_client_missing_access_token(responses):
    responses.add(responses_lib.POST, TOKEN_URL, json={"foo": "bar"}, status=200)
    oc = OAuthClient(client_id="a", client_secret="s", redirect_uri="https://x/cb")
    with pytest.raises(OkAuthError):
        oc.exchange_code("CODE")


def test_oauth_client_rejects_empty_code():
    oc = OAuthClient(client_id="a", client_secret="s", redirect_uri="https://x/cb")
    with pytest.raises(OkAuthError):
        oc.exchange_code("")


def test_oauth_client_rejects_empty_refresh():
    oc = OAuthClient(client_id="a", client_secret="s", redirect_uri="https://x/cb")
    with pytest.raises(OkAuthError):
        oc.refresh("")


def test_oauth_client_rejects_missing_init_args():
    with pytest.raises(OkAuthError):
        OAuthClient(client_id="", client_secret="s", redirect_uri="x")
