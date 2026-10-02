---
title: Broken access control
summary: Authentication proves who you are; authorisation decides what you may touch. Two bugs follow from forgetting the second.
order: 4
files: [access.py]
run: python access.py
hints:
  - "`idor_attack`: call the provided `fetch_vulnerable` as `alice` but pass the object id that belongs to `bob` - it returns the data without checking who owns it."
  - "`fetch_safe`: look up the object, and return its data only when its `owner` matches the requesting `user`; otherwise return `None`."
  - "`delete_user_safe`: allow the delete only when the actor's role is `admin`; otherwise raise `PermissionError`. Being logged in is not the same as being allowed."
  - "Both fixes are the same missing step: check that *this* user is permitted to do *this* thing to *this* object."
---

Logging a user in - **authentication** - is only half the job. The other half,
done on every single request, is **authorisation**: deciding whether this
already-identified user is allowed to do what they are asking. Forgetting it is
one of the most common and most serious web flaws, precisely because the login
works perfectly and everything looks fine.

## Insecure direct object references

A page shows your invoice at `/invoice?id=4792`. You change the number to
`4793` and see someone else's invoice. The server authenticated you - it knows
you are logged in - but never checked that invoice `4793` is *yours*. This is an
**IDOR**, and it needs no tools: just an id and the willingness to change it.

```python
def fetch(obj_id, user):
    return OBJECTS[obj_id]["data"]      # never checks OBJECTS[obj_id]["owner"]
```

## Missing function-level authorisation

The other half: a `/admin/delete-user` action that works for anyone who knows
the URL, because the code assumes only admins would ever reach it. Hiding a
button is not access control; the request can be made directly. **Authenticated
is not authorised** - a logged-in ordinary user is still not an admin.

## The defence

There is one fix behind both, applied on the server for every request: check
that *this* user is permitted to perform *this* action on *this* resource.
Ownership for data, role for privileged actions. It cannot live in the UI,
because the UI is not where the request is decided - the attacker sends the
request without ever loading your page.

## Your turn

`OBJECTS` (owned notes), `USERS` (with roles) and the vulnerable `fetch_vulnerable`
are provided. In `access.py`:

- `idor_attack()` - return the `(user, obj_id)` where `user` reads an object they
  do not own through `fetch_vulnerable`
- `fetch_safe(objects, obj_id, user)` - return the data only if `user` owns the
  object, else `None`
- `delete_user_safe(users, actor, target)` - delete `target` only if `actor` is
  an admin, else raise `PermissionError`
