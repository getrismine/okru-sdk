"""Общие фикстуры для тестов."""

from __future__ import annotations

import pytest
import responses as responses_lib

from okru import Client


@pytest.fixture
def responses():
    """Активный mock для requests. Используется в сетевых тестах."""
    with responses_lib.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def client():
    """Client с фиктивными credentials."""
    return Client(
        access_token="tok",
        application_key="APPKEY",
        application_secret_key="secret",
    )
