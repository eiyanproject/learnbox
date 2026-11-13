---
title: "Boss: Harden the login"
summary: A working login with every classic weakness in it. Fix all of them before it ships.
order: 4
files: [auth.py]
run: python -i auth.py
challenge:
  boss: true
  minutes: 35
  xp: 500
  requires:
    xp: 1800
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **boss round** | the longest arena round, combining several lessons |
| **plain-text password** | a password stored exactly as typed; anyone who reads the store has it |
| **salt** | a random value, different per user, mixed in before hashing |
| **slow hash** (KDF) | a hash made slow on purpose, here PBKDF2 with 100,000 iterations (Foundations lesson 3) |
| **record** | what is stored per user: the salt and the hash |
| **weak password** | here, shorter than 10 characters |
| **user enumeration** | finding out which user names exist, from different error messages |
| **generic error** | the same message, `"invalid credentials"`, whatever was wrong |
| **constant-time comparison** | one that takes the same time however much matches |
| **lockout** | refusing every login for an account after too many failures in a row |
| **failure counter** | how many failed logins in a row an account has had |
| **session token** | the random value a successful login returns; it stands for the user |
| **unpredictable** | made by `secrets`, so nobody can guess another user's token |
| **`AuthError`**, **`WeakPassword`**, **`LockedOut`** | the exceptions already defined at the top of `auth.py` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python -i auth.py` | runs your file, then leaves Python open so you can try the `Accounts` class |

### Python names

| Name | What it does |
|---|---|
| `class Accounts:` | the class to harden; keep its method names |
| `self.users[name]` | the stored record for one user |
| `secrets.token_bytes(16)` | a random 16-byte salt |
| `hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)` | the slow, salted hash |
| `hmac.compare_digest(a, b)` | compares the hashes in constant time |
| `secrets.token_hex(16)` | a new, unguessable session token |
| `raise AuthError("invalid credentials")` | the one message for every failed login |
| `self.sessions.pop(token, None)` | removes a session, doing nothing if it is not there |

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
