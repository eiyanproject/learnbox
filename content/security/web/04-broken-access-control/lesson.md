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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **authentication** | proving who you are: logging in |
| **authorisation** | deciding what an identified user may do |
| **access control** | the checks that enforce authorisation |
| **broken access control** | a missing or wrong check, so users can do or see what they should not; first in the OWASP Top 10 |
| **resource** (object) | a thing the site stores: an invoice, a note, a user account |
| **object ID** | the number or name that picks out a resource, as in `/invoice?id=4792` |
| **owner** | the user a resource belongs to |
| **IDOR** (insecure direct object reference) | the server returns whatever ID you ask for, without checking it is yours |
| **role** | a named level of access, such as `user` or `admin` |
| **privileged action** | something only some roles may do, such as deleting users |
| **function-level authorisation** | checking the role before running a privileged action |
| **UI** (user interface) | the pages and buttons; hiding a button there is not a check |
| **server-side check** | a check in the code that answers the request, which the user cannot skip |
| **deny by default** | refuse unless a rule clearly allows it |
| **`PermissionError`** | the Python error raised here when an action is not allowed |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python access.py` | runs your program: alice reads bob's note through the vulnerable fetch, then through the safe one |

### Python names

| Name | What it does |
|---|---|
| `OBJECTS`, `USERS` | given to you: dicts of notes (with owners) and users (with roles) |
| `fetch_vulnerable(obj_id, user)` | given to you: returns the note **without** checking the owner |
| `objects.get(obj_id)` | the item for that key, or `None` if there is none (no error) |
| `users.get(actor, {}).get("role")` | the actor's role, or `None` if the actor is unknown |
| `obj["owner"] != user` | `True` when the requester is not the owner |
| `raise PermissionError("...")` | stops with a "not allowed" error |
| `del users[target]` | removes that key from the dict |

---

Logging a user in, **authentication**, is only half the job. The other half,
done on **every** request, is **authorisation**: deciding whether this user,
whom we now know, is allowed to do what they are asking.

Forgetting it is one of the most common and most serious web flaws. "Broken
access control" is first in the OWASP Top 10, the best-known list of web
risks. It is easy to miss precisely because the login works perfectly and
everything looks fine.

## Insecure direct object references (IDOR)

A page shows your invoice at `/invoice?id=4792`. You change the number to
`4793` and see someone else's invoice. The server **authenticated** you: it
knows you are logged in. But it never checked that invoice 4793 is **yours**.

This is an **insecure direct object reference** (IDOR). It needs no tools,
just an ID and the curiosity to change it. In code, the mistake looks like
this:

```python
def fetch(obj_id, user):
    return OBJECTS[obj_id]["data"]      # never checks OBJECTS[obj_id]["owner"]
```

The function is given the user, and ignores them.

## Missing function-level authorisation

The second form is about actions rather than data. A page at
`/admin/delete-user` works for anyone who knows the address, because the
programmer assumed only admins would ever find it. The admin button was
hidden from ordinary users, but hiding a button is not access control: anyone
can send the request directly, as Web lesson 1 showed.

The rule: **authenticated is not authorised**. A logged-in ordinary user is
still not an admin.

## The defence

One fix covers both, applied **on the server**, on every request: check that
**this** user may do **this** action to **this** resource.

- For data: is the user the **owner** (or otherwise allowed)?
- For privileged actions: does the user have the right **role**?

The check cannot live in the user interface, because the interface is not
where the request is decided. An attacker sends the request without ever
loading your page.

OWASP's Authorization Cheat Sheet adds two habits:

- **Deny by default.** If no rule clearly allows it, refuse. An unknown user,
  or a missing role, means "no", never "probably fine".
- **Fail safely.** When a check fails, change nothing: refuse before doing
  any work.

## Your turn

`OBJECTS` (notes with owners), `USERS` (with roles) and the vulnerable
`fetch_vulnerable` are given to you. In `access.py`:

- `idor_attack()`: return a `(user, obj_id)` pair where `user` reads an
  object they do not own through `fetch_vulnerable`.
- `fetch_safe(objects, obj_id, user)`: return the data only if `user` owns the
  object, otherwise `None` (also `None` for an ID that does not exist).
- `delete_user_safe(users, actor, target)`: delete `target` from `users` only
  if `actor` is in `users` with the role `"admin"`. Otherwise, including when
  `actor` is not in `users` at all, raise `PermissionError` and change
  nothing.

Run it:

```text
alice reads object 2: bob's bank details
safe fetch of the same: None
```

## Check yourself

1. What is the difference between authentication and authorisation?
   *Authentication is who you are; authorisation is what you may do.*
2. You change `id=4792` to `id=4793` and see another customer's invoice.
   What is the flaw called?
   *An IDOR.*
3. Why is hiding the admin button not enough?
   *The request can be sent directly without the button.*
4. Where must the access check happen?
   *On the server, for every request.*
5. `delete_user_safe` is called by an actor who is not in `users`. What
   should happen?
   *Deny by default: raise `PermissionError` and delete nothing.*
