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

Here is a password routine with both mistakes from the Foundations password
lesson at once: it stores `sha256(password)` - fast and unsalted - and checks it
with `==`, which leaks through its timing. An attacker who steals the store
cracks every common password instantly, and the comparison hands out a timing
side channel for free. Rebuild it correctly.

## The brief

Replace the storage and the check:

- **Storage** - `make_record(password)` must use a fresh random **salt** and a
  **slow** key-derivation function (`hashlib.pbkdf2_hmac`), returning a record
  that carries the salt and iteration count alongside the derived hash.
- **Verification** - `check_password(attempt, record)` must recompute from the
  attempt using the record's salt and iterations, and compare in **constant
  time** with `hmac.compare_digest`.

Two users with the same password must end up with different records, and a
correct password must still verify. The two flaws compound: a fast unsalted
hash lets an attacker who steals the store test billions of guesses a second,
and the `==` comparison is a timing side channel. Against a hash the timing leak
is far less useful than against a token (the attacker cannot steer the hash's
bytes), so the storage flaw is the serious one - but a constant-time compare is
the habit to keep, and a review that leaves either in place is not finished.

## Your turn

In `pwcheck.py`, implement `make_record(password)` and
`check_password(attempt, record)`. `password` and `attempt` are strings. The
record is a dict with exactly the keys the checks read:

- `"salt"` - the random salt as a hex string (`secrets.token_bytes(16).hex()`)
- `"iterations"` - the PBKDF2 iteration count, an integer of at least 10,000
- `"hash"` - `hashlib.pbkdf2_hmac("sha256", password.encode(), salt,
  iterations)` as a hex string

`check_password` returns a bool.
