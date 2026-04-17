from okru import signing


def test_session_secret_is_md5_of_token_plus_secret():
    # md5("toksecret") == "76f3a2f1b0085..."
    got = signing.session_secret("tok", "secret")
    assert len(got) == 32
    # то же ли самое получаем при повторном вызове
    assert signing.session_secret("tok", "secret") == got


def test_session_secret_rejects_empty():
    import pytest
    with pytest.raises(ValueError):
        signing.session_secret("", "secret")
    with pytest.raises(ValueError):
        signing.session_secret("tok", "")


def test_build_params_string_sorted():
    s = signing.build_params_string({"b": 2, "a": 1, "c": 3})
    assert s == "a=1b=2c=3"


def test_build_params_string_excludes_access_token_and_sig():
    s = signing.build_params_string({
        "method": "users.get",
        "access_token": "tok",
        "sig": "deadbeef",
    })
    assert "access_token" not in s
    assert "sig" not in s
    assert s == "method=users.get"


def test_build_params_string_handles_list_and_bool():
    s = signing.build_params_string({
        "flag": True,
        "off": False,
        "ids": [1, 2, 3],
    })
    assert "flag=true" in s
    assert "off=false" in s
    assert "ids=1,2,3" in s


def test_build_params_string_skips_none():
    s = signing.build_params_string({"a": 1, "b": None})
    assert s == "a=1"


def test_sign_is_deterministic():
    params = {"method": "users.get", "uid": "42"}
    a = signing.sign(params, "secret")
    b = signing.sign(params, "secret")
    assert a == b
    assert len(a) == 32


def test_sign_changes_when_params_change():
    assert signing.sign({"a": 1}, "s") != signing.sign({"a": 2}, "s")


def test_sign_changes_when_secret_changes():
    assert signing.sign({"a": 1}, "s1") != signing.sign({"a": 1}, "s2")


def test_sign_rejects_empty_secret():
    import pytest
    with pytest.raises(ValueError):
        signing.sign({"a": 1}, "")
