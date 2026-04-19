from okru import FeedItem, Group, User


def test_user_from_dict_common_fields():
    u = User.from_dict({
        "uid": "42",
        "first_name": "Иван",
        "last_name": "Петров",
        "age": 30,
        "online": "web",
    })
    assert u.uid == "42"
    assert u.first_name == "Иван"
    assert u.full_name == "Иван Петров"
    assert u.age == 30


def test_user_full_name_handles_missing_parts():
    assert User.from_dict({"uid": "1", "first_name": "Аня"}).full_name == "Аня"
    assert User.from_dict({"uid": "1"}).full_name == ""


def test_user_preserves_raw_dict():
    data = {"uid": "1", "custom_field": "x"}
    u = User.from_dict(data)
    assert u.raw["custom_field"] == "x"


def test_group_from_dict():
    g = Group.from_dict({
        "uid": "g1",
        "name": "Кулинарная",
        "members_count": 1200,
        "pic_avatar": "https://x/pic.jpg",
    })
    assert g.uid == "g1"
    assert g.members_count == 1200
    assert g.pic_avatar.startswith("https")


def test_feeditem_from_dict_with_author_ref():
    fi = FeedItem.from_dict({
        "id": "post-1",
        "type": "POST",
        "date": "2026-04-20T10:00:00",
        "message": "привет",
        "author_ref": "user:42",
    })
    assert fi.id == "post-1"
    assert fi.type == "POST"
    assert fi.author_ref == "user:42"


def test_feeditem_falls_back_to_owner_ref():
    fi = FeedItem.from_dict({"id": "1", "owner_ref": "group:99"})
    assert fi.author_ref == "group:99"


def test_feeditem_missing_fields_ok():
    fi = FeedItem.from_dict({})
    assert fi.id == ""
    assert fi.type == "unknown"
    assert fi.message is None
