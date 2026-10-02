OBJECTS = {
    1: {"owner": "alice", "data": "alice's private note"},
    2: {"owner": "bob", "data": "bob's bank details"},
}

USERS = {
    "alice": {"role": "user"},
    "bob": {"role": "user"},
    "root": {"role": "admin"},
}


def fetch_vulnerable(obj_id, user):
    # VULNERABLE: returns the object without checking who owns it.
    return OBJECTS[obj_id]["data"]


def idor_attack():
    # alice simply asks for object 2, which belongs to bob. No tool needed -
    # the server never checks ownership, so changing the id is the whole attack.
    return ("alice", 2)


def fetch_safe(objects, obj_id, user):
    # The missing check: the requester must own the object.
    obj = objects.get(obj_id)
    if obj is None or obj["owner"] != user:
        return None
    return obj["data"]


def delete_user_safe(users, actor, target):
    # Authenticated is not authorised: only an admin may delete a user.
    if users.get(actor, {}).get("role") != "admin":
        raise PermissionError(f"{actor} is not allowed to delete users")
    del users[target]


if __name__ == "__main__":
    u, oid = idor_attack()
    print(f"{u} reads object {oid}:", fetch_vulnerable(oid, u))
    print("safe fetch of the same:", fetch_safe(OBJECTS, oid, u))
