---
title: "Boss: Harden the login"
summary: A working login with every classic weakness in it. Fix all of them before it ships.
order: 3
files: [auth.py]
run: python -i auth.py
challenge:
  boss: true
  minutes: 35
  xp: 500
  requires:
    xp: 1800
---

`auth.py` works. It also stores passwords as they were typed, tells an
attacker which user names exist, lets them guess for ever, and hands out
tokens anyone could predict. It ships tonight unless you fix it.

## The task

Harden the `Accounts` class. Its methods keep their names; the exception
classes at the top of the file are already there.

### 1. Never store the password

`register(name, password)` must keep a **salted, slow hash**, not the
password: a fresh random salt per user (`secrets.token_bytes(16)`) and
`hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)`. Keep the
salt and the hash in `self.users[name]`. Two users with the same password
must not end up with the same record, and the password must not be
recoverable from anything the object holds.

### 2. Refuse weak passwords and duplicate names

`register` raises `WeakPassword` for a password shorter than 10 characters,
and `AuthError` for a name that is already registered - without replacing
the existing account.

### 3. Say nothing about which part was wrong

A failed `login` raises `AuthError` with exactly the message
`"invalid credentials"`, whether the name is unknown or the password is
wrong.

### 4. Compare in constant time

Compare the computed hash with the stored one using `hmac.compare_digest`,
not `==`.

### 5. Lock out guessing

After **5 failed logins in a row** for a registered name, the account is
locked: every further `login` for it raises `LockedOut`, even with the right
password, until `unlock(name)` is called. A successful login sets the count
back to zero. Unknown names are never locked; they just get
`"invalid credentials"`.

### 6. Unpredictable sessions

`login` returns a new token from `secrets.token_hex(16)` each time.
`whoami(token)` returns the name the token belongs to, or `None`.
`logout(token)` ends that session; logging out an unknown token does
nothing.

```python
accounts = Accounts()
accounts.register("ana", "correct horse battery")
token = accounts.login("ana", "correct horse battery")
accounts.whoami(token)      # "ana"
accounts.logout(token)
accounts.whoami(token)      # None
```
