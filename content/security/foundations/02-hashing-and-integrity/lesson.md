---
title: Hashing and integrity
summary: What a hash proves and what it does not, why an unsalted password hash falls to a lookup, and the salt and HMAC that fix it.
order: 2
files: [integrity.py]
run: python integrity.py
hints:
  - "`sha256_hex(data)`: `import hashlib`, then `hashlib.sha256(data).hexdigest()`."
  - "`crack(target_hex, words)`: hash each word and return the first whose hash equals the target - this is why an unsalted hash of a common password is no protection."
  - "`salted_hash(password, salt)`: hash the salt concatenated with the password bytes. The salt is why two people with the same password get different hashes."
  - "`verify_hmac`: recompute the HMAC over the message with the key and compare with `hmac.compare_digest`, never `==`."
---

A **hash** turns any input into a fixed-length fingerprint. A good one -
SHA-256 - has two properties that matter: the same input always gives the same
output, and you cannot work backwards from the output to the input.

```pycon
>>> import hashlib
>>> hashlib.sha256(b"hello").hexdigest()
'2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
>>> hashlib.sha256(b"hello!").hexdigest()     # one character more
'ce06092fb948d9ffac7d1a376e404b26b7575bcc11ee05a4615fef4fec3a308b'
```

Change one character and the whole fingerprint changes - which is what lets a
hash catch tampering.

This is **integrity**, not secrecy. A hash tells you whether data changed: store
the hash, recompute it later, and if they differ the data was altered. It is
how downloads are checked and how files are compared.

## Where hashing is misused

Storing a password as `sha256(password)` feels safe - the hash cannot be
reversed, after all. But "cannot be reversed" is not "cannot be guessed". An
attacker who steals the hashes does not reverse them; they hash every common
password and compare. Because the hash is unsalted and fast, the same password
always produces the same hash, and a precomputed table turns the whole thing
into a dictionary lookup.

You will write that attack. It is three lines, and that is the point: an
unsalted hash of a guessable password protects nothing.

## The defences

**Salt** - a unique random value stored beside each hash and mixed in before
hashing. Now two users with the same password have different hashes, and one
precomputed table no longer works against everyone at once.

**HMAC** - a keyed hash, used to prove a message came from someone holding the
key and was not altered. The receiver recomputes it and compares. The
comparison must be **constant-time** (`hmac.compare_digest`): a normal `==`
returns as soon as two bytes differ, and that tiny timing difference can leak
the correct value one byte at a time.

(Salt and a fast hash are only half the password story - the hash must also be
*slow*. That is the next lesson.)

## Your turn

In `integrity.py`:

- `sha256_hex(data)` - the SHA-256 hex digest of `data` (bytes)
- `tampered(data, expected_hex)` - `True` when `data` does not hash to the
  expected digest
- `crack(target_hex, words)` - the word in `words` whose SHA-256 equals
  `target_hex`, or `None`; this is the attack on an unsalted hash
- `salted_hash(password, salt)` - SHA-256 of `salt + password` (both bytes)
- `verify_hmac(key, message, tag_hex)` - `True` when `tag_hex` is a valid
  SHA-256 HMAC of `message` under `key`, compared in constant time
