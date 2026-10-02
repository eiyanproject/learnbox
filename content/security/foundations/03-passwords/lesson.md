---
title: How passwords are stored and attacked
summary: Why a fast hash is the problem, what entropy really measures, the slow KDF that fixes storage, and comparing secrets without leaking their length.
order: 3
files: [passwords.py]
run: python passwords.py
hints:
  - "`estimate_bits`: find which character classes appear (lower 26, upper 26, digits 10, other 33), add up the pool size, and return `len(password) * log2(pool)`. Empty password is 0 bits."
  - "`slow_hash`: `hashlib.pbkdf2_hmac('sha256', password, salt, iterations)` then `.hex()`. The iteration count is what makes it slow on purpose."
  - "`constant_time_equal`: if the lengths differ return False, then OR together `x ^ y` for every pair and return whether the total is 0 - no early exit on the first difference."
  - "`is_strong`: at least 60 estimated bits AND the lowercased password is not one of the common ones."
---

The last lesson ended on a cliffhanger: salt is necessary but not sufficient.
The other half is **speed**, and it is counter-intuitive - a *slower* hash is a
*safer* hash.

## Why fast hashing loses

SHA-256 is built to be fast: a modern machine computes **billions** per second.
That is exactly what you want for checking a download and exactly what you do
*not* want for passwords, because the attacker who stole your hashes runs those
same billions per second against them. Salt stops one precomputed table from
cracking every account at once, but it does nothing to slow down guessing a
single account.

The fix is a **key derivation function** - PBKDF2, scrypt, argon2 - deliberately
built to be slow, by repeating the hash tens or hundreds of thousands of times:

```python
hashlib.pbkdf2_hmac("sha256", password, salt, 200_000)
```

Now each guess costs the attacker 200,000 hashes instead of one. The honest
user logging in pays that cost once and never notices; the attacker trying a
billion guesses pays it a billion times and grinds to a halt. That asymmetry is
the entire design.

## Entropy, and what it does not know

Password strength is measured in **bits of entropy** - the base-2 logarithm of
how many passwords an attacker would have to try. A rough estimate is the
character-pool size raised to the length, so length matters far more than
"complexity":

- `P@ss1!` - 6 characters, every class: about 39 bits
- `correcthorsebatterystaple` - 25 lowercase letters: about 118 bits

The long passphrase is astronomically stronger despite being "just letters".

But this estimate assumes the characters are **random**, and real passwords are
not. `password1234567890` scores high by this maths and is worthless, because
it is a dictionary word plus a predictable suffix - an attacker's word list
tries it in seconds. This is why entropy estimation is only a first gate, and
real systems *also* reject anything appearing in breach corpora. Treat the
number as a floor on an ideal case, never a guarantee.

## Comparing without leaking

Checking a password or a token means comparing the stored value with the
supplied one. A plain `==` on secrets stops at the first differing byte, and the
time it takes therefore reveals how many leading bytes were right - a **timing
side channel** that lets an attacker recover a secret one byte at a time. The
fix is a comparison that always inspects every byte.

## Your turn

In `passwords.py`:

- `estimate_bits(password)` - estimated entropy in bits, as described above
- `slow_hash(password, salt, iterations)` - the PBKDF2-HMAC-SHA256 derived key
  as a hex string (`password` and `salt` are bytes)
- `constant_time_equal(a, b)` - compare two byte strings without an early exit
- `is_strong(password)` - at least 60 estimated bits and not a common password
