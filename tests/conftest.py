"""Общие фикстуры для тестов."""

from __future__ import annotations

import pytest
import responses as responses_lib


@pytest.fixture
def responses():
    """Активный mock для requests."""
    with responses_lib.RequestsMock() as rsps:
        yield rsps
