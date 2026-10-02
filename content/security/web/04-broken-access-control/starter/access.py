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
    # Return (user, obj_id) where user reads an object they do not own.
    pass


def fetch_safe(objects, obj_id, user):
    # Return the data only if user owns the object, else None.
    pass


def delete_user_safe(users, actor, target):
    # Delete target only if actor is an admin, else raise PermissionError.
    pass


if __name__ == "__main__":
    u, oid = idor_attack()
    print(f"{u} reads object {oid}:", fetch_vulnerable(oid, u))
    print("safe fetch of the same:", fetch_safe(OBJECTS, oid, u))
