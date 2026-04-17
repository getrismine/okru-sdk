from okru.errors import (
    OkApiError,
    OkInvalidAccessTokenError,
    OkInvalidSessionError,
    OkParamError,
    OkPermissionDeniedError,
    OkRateLimitError,
    from_response,
)


def test_from_response_maps_known_codes():
    cases = [
        (100, OkParamError),
        (102, OkInvalidSessionError),
        (103, OkInvalidAccessTokenError),
        (104, OkPermissionDeniedError),
        (105, OkParamError),
        (454, OkParamError),
        (1002, OkRateLimitError),
    ]
    for code, cls in cases:
        exc = from_response({"error_code": code, "error_msg": "boom"})
        assert isinstance(exc, cls), f"код {code} должен быть {cls.__name__}"
        assert exc.code == code
        assert exc.message == "boom"


def test_from_response_unknown_code_falls_back_to_base():
    exc = from_response({"error_code": 9999, "error_msg": "?"})
    assert type(exc) is OkApiError
    assert exc.code == 9999


def test_from_response_preserves_raw_payload():
    payload = {"error_code": 100, "error_msg": "bad", "extra": {"field": "uid"}}
    exc = from_response(payload)
    assert exc.data == payload


def test_error_str_includes_code_and_message():
    exc = from_response({"error_code": 102, "error_msg": "invalid session"})
    assert "102" in str(exc)
    assert "invalid session" in str(exc)


def test_from_response_defaults_on_missing_fields():
    exc = from_response({})
    assert exc.code == 0
    assert "неизвестная" in exc.message
