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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **hash** (hash function) | a calculation that turns any input, of any size, into a short fixed-size value |
| **digest** | the value a hash produces; for SHA-256, 32 bytes, shown as 64 hex digits |
| **fingerprint** | another word for a digest: small, and different for every different input |
| **SHA-256** | a modern, standard hash from the SHA-2 family; 256 bits of output |
| **MD5, SHA-1** | older hashes that are broken: people can make two inputs with the same digest, so never rely on them for security |
| **deterministic** | the same input always gives the same output |
| **one-way** (pre-image resistance) | given a digest, there is no way to calculate the input back |
| **collision** | two different inputs with the same digest; a good hash makes finding one practically impossible |
| **avalanche effect** | changing one bit of the input changes about half the bits of the digest |
| **integrity** | knowing that data has not been changed |
| **tampering** | changing data without permission |
| **dictionary attack** | guessing a password by hashing every word in a list and comparing |
| **wordlist** | a list of common passwords used for such guessing |
| **precomputed table** (rainbow table) | digests of millions of passwords, calculated once in advance, so cracking becomes a lookup |
| **salt** | a random value, different for each user, stored beside the hash and mixed in before hashing |
| **HMAC** | a keyed hash: a digest that only someone holding the secret key can make or check |
| **key** | a secret value shared by the people who make and check an HMAC |
| **tag** (MAC) | the value an HMAC produces, sent with the message |
| **forgery** | making a valid-looking tag without the key |
| **constant-time comparison** | a comparison that takes the same time however many characters match |
| **timing attack** | learning a secret by measuring how long a program takes to answer |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `sha256sum file` | prints the SHA-256 digest of a file, then its name |
| `sha256sum -c file.sha256` | checks files against digests saved in `file.sha256`, printing `OK` or `FAILED` |
| `python integrity.py` | runs your finished program: it "steals" a hash and cracks it |

### Python names

| Name | What it does |
|---|---|
| `import hashlib` | loads Python's hashing module |
| `hashlib.sha256(data)` | a SHA-256 hash object for the bytes `data` |
| `.hexdigest()` | the digest as a string of hex digits |
| `b"..."` | a bytes literal; hashing works on bytes, not text |
| `salt + password` | two bytes objects joined end to end |
| `import hmac` | loads Python's HMAC module |
| `hmac.new(key, message, hashlib.sha256)` | an HMAC object using SHA-256 |
| `hmac.compare_digest(a, b)` | `True` when `a` equals `b`, compared in constant time |
| `for word in words:` | each item in a list in turn |
| `return None` | the function's way of saying "not found" |

---

A **hash** takes any input, one byte or a whole disk image, and turns it into
a short fixed-size value called a **digest**. Think of it as a fingerprint of
the data. **SHA-256**, the standard choice today, always gives 32 bytes,
written as 64 hex digits.

A good hash has three properties that matter here:

1. **Deterministic**: the same input always gives the same digest.
2. **One-way**: from the digest you cannot calculate the input.
3. **Avalanche**: change one character and the whole digest changes, not
   just one part of it.

```pycon
>>> import hashlib
>>> hashlib.sha256(b"hello").hexdigest()
'2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'
>>> hashlib.sha256(b"hello!").hexdigest()     # one character more
'ce06092fb948d9ffac7d1a376e404b26b7575bcc11ee05a4615fef4fec3a308b'
>>> len(hashlib.sha256(b"").hexdigest())      # even empty input: 64 hex digits
64
```

The two digests share nothing you could use to tell that the inputs were
almost the same. That is what lets a hash catch tampering.

## What a hash is for: integrity

A hash gives **integrity**, not secrecy. It answers one question: has this
data changed?

1. Hash the data while you know it is good, and keep the digest.
2. Later, hash it again.
3. If the two digests differ, the data was altered.

This is how downloads are checked. A project publishes the SHA-256 of its
installer; you run `sha256sum` on the file you downloaded and compare. If even
one byte was damaged or replaced on the way, the digests will not match.

A hash does **not** hide anything: anyone can hash anything. And it only
helps if the digest you compare against is itself trustworthy. If an
attacker can replace both the file and the published digest, the check
passes. (That is what HMAC, below, and signatures in the Crypto section fix.)

Older hashes, **MD5** and **SHA-1**, are broken: researchers can make two
different files with the same digest, a **collision**. You will still see
them in old systems; do not use them for anything that matters.

## Where hashing goes wrong: passwords

A website should not store passwords as they are, so many store
`sha256(password)` instead. That sounds safe, because the hash cannot be
reversed. But "cannot be reversed" is not "cannot be guessed".

An attacker who steals the database does not need to reverse anything. They
take a **wordlist** of common passwords, hash every word, and compare each
result with the stolen digests. When one matches, they know the password.
This is a **dictionary attack**, and SHA-256 makes it fast: an ordinary
graphics card computes billions of SHA-256 digests a second.

It gets worse. With no salt, the same password always gives the same digest,
so `password123` has the same digest in every website's database:

```pycon
>>> from integrity import sha256_hex
>>> sha256_hex(b"password123")
'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'
```

Attackers calculate these digests once, for millions of passwords, and keep
them in **precomputed tables**. Cracking then becomes a lookup: search for the
digest, read off the password.

You will write the dictionary attack yourself. It is three lines long, and
that is the lesson: an unsalted hash of a guessable password protects nothing.

## The first fix: salt

A **salt** is a random value, different for every user, stored next to their
hash. It is mixed in before hashing: the stored value is
`sha256(salt + password)`. The salt is not secret; its job is only to be
different for everyone.

```pycon
>>> from integrity import salted_hash
>>> salted_hash(b"password123", b"\x9f\x1a")
'56544f04dec4060a82f4fdfa555660dfc0ca119cd0176315404db446fa905b39'
>>> salted_hash(b"password123", b"\x03\xc4")     # same password, another user
'5dc4488d8bbd3e7e48c974b34a963cdf3ba621a4d50a2a8da98509c465f4687b'
```

Now two users with the same password have different digests, and a
precomputed table is useless: it would need a separate table for every salt.
The attacker has to guess each user's password separately.

Salt does **not** slow each guess down, though. One salted SHA-256 is still
billions of guesses a second, so a weak password still falls. The other half
of the fix, a deliberately **slow** hash, is the next lesson.

## Proving who sent a message: HMAC

A plain hash cannot tell you who made it. An **HMAC** is a hash that also
uses a secret **key**: only someone holding the key can produce the right
**tag** for a message, and only someone holding it can check one.

```pycon
>>> import hmac
>>> hmac.new(b"secret-key", b"transfer 100", hashlib.sha256).hexdigest()
'2334202fc2c257d85383a17593a96c37da67e9878f1d74e4ebc14124689005ef'
```

The sender sends the message with its tag. The receiver, who has the same
key, recomputes the tag over the message and compares. If someone changed
`transfer 100` to `transfer 900`, the tags no longer match, and without the
key they cannot calculate the new one. That is **integrity and
authenticity** together. Web sessions, signed cookies and API requests use
HMACs this way.

### Why the comparison must be constant-time

The obvious way to compare two tags is `==`. But `==` stops at the first
character that differs, so a tag that is right in its first ten characters
takes slightly longer to reject than one that is wrong in its first. An
attacker who sends millions of guesses and measures the time can use that
difference to find the correct tag one character at a time. This is a
**timing attack**.

`hmac.compare_digest(a, b)` always looks at every character, so it takes the
same time whether the first or the last one is wrong. Use it whenever you
compare a secret value.

## Your turn

In `integrity.py`:

- `sha256_hex(data)`: the SHA-256 hex digest of `data` (bytes).
- `tampered(data, expected_hex)`: `True` when `data` does **not** hash to
  the expected digest.
- `crack(target_hex, words)`: the word in `words` whose SHA-256 equals
  `target_hex`, or `None` if there is none. This is the attack on an unsalted
  hash.
- `salted_hash(password, salt)`: SHA-256 of `salt + password` (both bytes),
  as hex.
- `verify_hmac(key, message, tag_hex)`: `True` when `tag_hex` is a valid
  SHA-256 HMAC of `message` under `key`, compared with
  `hmac.compare_digest`.

Run it and the program cracks a "stolen" hash:

```text
stolen hash: ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f
cracked to: b'password123'
```

## Check yourself

1. Does a SHA-256 digest keep data secret?
   *No. It shows whether data changed; anyone can hash anything.*
2. The attacker cannot reverse SHA-256. How do they still recover
   `password123` from its digest?
   *They hash guesses from a wordlist and compare.*
3. What does a salt stop, and what does it not stop?
   *It stops one precomputed table from cracking everyone; it does not make
   each guess slower.*
4. What does an HMAC prove that a plain hash cannot?
   *That the message was made by someone holding the key.*
5. Why `hmac.compare_digest` and not `==`?
   *`==` stops at the first difference, and the timing leaks how much was
   right.*
