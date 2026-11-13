---
title: "Challenge: the broken password check"
summary: A password routine with the two classic mistakes - a fast unsalted hash and a leaky comparison. Rebuild it properly.
order: 3
files: [pwcheck.py]
run: python pwcheck.py
hints:
  - "Storage: a per-user random salt and a slow KDF (pbkdf2_hmac with many iterations), never a bare sha256. Keep the salt and iteration count in the record."
  - "Verification: recompute from the attempt and compare with hmac.compare_digest, never ==."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **password store** | the database of saved password records |
| **record** | what is saved for one user: here the salt, the iteration count and the hash |
| **fast hash** | a hash like SHA-256, built for speed: billions of guesses a second |
| **unsalted** | every user's password hashed the same way, so equal passwords give equal hashes |
| **salt** | a random value, different for each user, mixed in before hashing (Foundations lesson 2) |
| **key derivation function** (KDF) | a hash made slow on purpose, for passwords (Foundations lesson 3) |
| **PBKDF2** | the KDF built into Python, which repeats HMAC many times |
| **iterations** | how many times PBKDF2 repeats; more is slower for every guess |
| **derived hash** | what the KDF produces from the password and salt |
| **constant-time comparison** | one that takes the same time however much matches |
| **timing side channel** | a leak through how long a comparison takes |
| **hex string** | bytes written as hex digits, so they can be stored as text |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python pwcheck.py` | runs your program: checks a right and a wrong password against a new record |

### Python names

| Name | What it does |
|---|---|
| `ITERATIONS` | given to you: the iteration count to use, 100,000 |
| `secrets.token_bytes(16)` | 16 random bytes, for the salt |
| `.hex()`, `bytes.fromhex(s)` | bytes to a hex string, and back |
| `password.encode()` | the password as bytes |
| `hashlib.pbkdf2_hmac("sha256", pw, salt, iterations)` | the derived hash, as bytes |
| `record["salt"]` | a value from the record dict |
| `hmac.compare_digest(a, b)` | `True` when equal, compared in constant time |

---

Here is a password routine with both mistakes from the Foundations lessons
at once:

1. It stores `sha256(password)`: a **fast**, **unsalted** hash.
2. It checks a login attempt with `==`.

An attacker who steals the **password store** cracks every common password
almost at once, because each guess costs one fast hash, and equal passwords
have equal hashes. And the `==` comparison leaks through its timing. Your job
is to rebuild the routine correctly.

## The brief

Replace both the storage and the check.

**Storage.** `make_record(password)` must use a fresh, random **salt** for
every record, and a **slow** key derivation function,
`hashlib.pbkdf2_hmac`. The record keeps the salt and the iteration count
alongside the **derived hash**, because the check will need both to repeat the
calculation.

**Verification.** `check_password(attempt, record)` must recompute the hash
from the attempt, using the record's own salt and iteration count, and compare
it with the stored hash in **constant time**, using `hmac.compare_digest`.

Two users with the same password must end up with different records, and a
correct password must still verify.

### Which flaw matters more

The two flaws add up, but they are not equal. The fast, unsalted hash lets an
attacker with a stolen store test billions of guesses a second: that is the
serious one. The `==` leak matters much less here than for a token, because
the attacker cannot choose the bytes of a hash to probe it. Still, a
constant-time comparison costs nothing and is the habit to keep. A review that
leaves either flaw in place is not finished.

## Your turn

In `pwcheck.py`, write `make_record(password)` and
`check_password(attempt, record)`. `password` and `attempt` are strings.
The record is a dict with exactly the keys the checks read:

- `"salt"`: the random salt as a hex string (`secrets.token_bytes(16).hex()`);
- `"iterations"`: the PBKDF2 iteration count, an integer of at least 10,000;
- `"hash"`: `hashlib.pbkdf2_hmac("sha256", password.encode(), salt,
  iterations)` as a hex string.

`check_password` returns `True` or `False`.

Run it:

```text
valid: True
wrong: False
```

## Check yourself

1. Why must every record have its own salt?
   *So equal passwords give different hashes, and one table cannot crack
   them all.*
2. Why store the salt and the iteration count in the record?
   *The check needs both to repeat the same calculation.*
3. Which of the two flaws is more serious here, and why?
   *The fast unsalted hash: it makes stolen records quick to crack.*
