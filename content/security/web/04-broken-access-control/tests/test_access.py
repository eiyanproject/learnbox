import pytest
from access import OBJECTS, USERS, fetch_vulnerable, idor_attack, fetch_safe, delete_user_safe


def test_idor_attack_reads_someone_elses_object():
    user, obj_id = idor_attack()
    # The attack returns real data the requester does not own.
    assert fetch_vulnerable(obj_id, user) == OBJECTS[obj_id]["data"]
    assert OBJECTS[obj_id]["owner"] != user


def test_fetch_safe_allows_the_owner():
    assert fetch_safe(OBJECTS, 1, "alice") == "alice's private note"
    assert fetch_safe(OBJECTS, 2, "bob") == "bob's bank details"


def test_fetch_safe_blocks_a_non_owner():
    assert fetch_safe(OBJECTS, 2, "alice") is None


def test_fetch_safe_blocks_the_recorded_attack():
    user, obj_id = idor_attack()
    assert fetch_safe(OBJECTS, obj_id, user) is None


def test_fetch_safe_unknown_object():
    assert fetch_safe(OBJECTS, 999, "alice") is None


def test_delete_requires_admin():
    users = {"alice": {"role": "user"}, "root": {"role": "admin"}, "victim": {"role": "user"}}
    with pytest.raises(PermissionError):
        delete_user_safe(users, "alice", "victim")
    assert "victim" in users  # still there


def test_admin_can_delete():
    users = {"root": {"role": "admin"}, "victim": {"role": "user"}}
    delete_user_safe(users, "root", "victim")
    assert "victim" not in users


def test_unknown_actor_is_not_admin():
    users = {"victim": {"role": "user"}}
    with pytest.raises(PermissionError):
        delete_user_safe(users, "ghost", "victim")
