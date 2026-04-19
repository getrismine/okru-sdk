"""Тесты для ресурсов users/friends/group/stream.

Общие: используют фикстуру ``client`` и мокают API через ``responses``.
"""

import pytest
import responses as responses_lib

from okru.client import API_BASE


def _mock(responses, payload, status=200):
    responses.add(responses_lib.GET, API_BASE, json=payload, status=status)


# -- users --------------------------------------------------------------------


def test_users_get_current_user(client, responses):
    _mock(responses, {"uid": "42", "first_name": "И", "last_name": "П"})
    u = client.users.get_current_user()
    assert u.uid == "42"
    assert u.full_name == "И П"


def test_users_get_info_empty_short_circuits(client, responses):
    assert client.users.get_info([]) == []
    # ни одного HTTP-вызова не должно быть
    assert len(responses.calls) == 0


def test_users_get_info_multiple(client, responses):
    _mock(responses, [
        {"uid": "1", "first_name": "A"},
        {"uid": "2", "first_name": "B"},
    ])
    users = client.users.get_info(["1", "2"])
    assert [u.first_name for u in users] == ["A", "B"]


# -- friends ------------------------------------------------------------------


def test_friends_get_string_list(client, responses):
    _mock(responses, ["1", "2", "3"])
    assert client.friends.get() == ["1", "2", "3"]


def test_friends_get_object_list(client, responses):
    _mock(responses, [{"uid": "1"}, {"uid": "2"}])
    assert client.friends.get() == ["1", "2"]


def test_friends_mutual_requires_target(client):
    with pytest.raises(ValueError):
        client.friends.get_mutual("")


def test_friends_mutual(client, responses):
    _mock(responses, ["5", "6"])
    assert client.friends.get_mutual("42") == ["5", "6"]


# -- group --------------------------------------------------------------------


def test_group_get_info_empty(client, responses):
    assert client.group.get_info([]) == []


def test_group_get_info(client, responses):
    _mock(responses, [{"uid": "g1", "name": "X", "members_count": 100}])
    groups = client.group.get_info(["g1"])
    assert groups[0].uid == "g1"
    assert groups[0].members_count == 100


def test_group_get_members_requires_id(client):
    with pytest.raises(ValueError):
        client.group.get_members("")


def test_group_get_members(client, responses):
    _mock(responses, {"members": [{"userId": "1"}, {"userId": "2"}], "anchor": "NEXT"})
    result = client.group.get_members("g1")
    assert result["anchor"] == "NEXT"


# -- stream -------------------------------------------------------------------


def test_stream_get_single_page(client, responses):
    _mock(responses, {
        "feeds": [{"id": "p1", "type": "POST", "message": "hi"}],
        "anchor": None,
    })
    items, anchor = client.stream.get(count=5)
    assert len(items) == 1
    assert items[0].message == "hi"
    assert anchor is None


def test_stream_iter_feed_paginates(client, responses):
    _mock(responses, {
        "feeds": [{"id": "1", "type": "POST"}, {"id": "2", "type": "POST"}],
        "anchor": "NEXT",
    })
    _mock(responses, {
        "feeds": [{"id": "3", "type": "POST"}],
        "anchor": None,
    })
    got = list(client.stream.iter_feed(page_size=2))
    assert [x.id for x in got] == ["1", "2", "3"]
    assert len(responses.calls) == 2


def test_stream_iter_feed_respects_max_items(client, responses):
    _mock(responses, {
        "feeds": [{"id": str(i), "type": "POST"} for i in range(5)],
        "anchor": "NEXT",
    })
    got = list(client.stream.iter_feed(page_size=5, max_items=3))
    assert len(got) == 3
    # второй страницы запрашивать не должны
    assert len(responses.calls) == 1


def test_stream_iter_feed_stops_on_empty_page(client, responses):
    _mock(responses, {"feeds": [], "anchor": None})
    assert list(client.stream.iter_feed()) == []
