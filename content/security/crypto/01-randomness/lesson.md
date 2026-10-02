---
title: Randomness that can be trusted
summary: The difference between random and secrets, why a predictable generator undoes a whole system, and reproducing a weak token to prove it.
order: 1
files: [rng.py]
run: python rng.py
hints:
  - "`secure_token`: `import secrets`, then `secrets.token_hex(n_bytes)` - a string twice as long as the byte count."
  - "`weak_token`: `random.Random(seed).getrandbits(32)`. The same seed always gives the same number, which is exactly the flaw."
  - "`predict`: make one `random.Random(seed)`, pull `n` values from it in a row, and return the last. A server reusing a guessable seed hands you its whole sequence."
  - "`enough_entropy`: 16 bytes is 128 bits, the usual floor for a token."
---

Almost every security mechanism rests on an attacker being unable to **guess** a
value: a session token, a password-reset link, a key, a nonce. That guarantee
comes entirely from the quality of the randomness, and this is a place
beginners reach for the wrong tool without knowing it.

## Two generators, one dangerous

Python has two, and they look interchangeable:

- `random` is a **pseudo-random** generator for simulations and games. It is
  fast, it is reproducible from its seed, and it is **predictable**. Never use
  it for anything an attacker should not guess.
- `secrets` is a **cryptographically secure** generator, drawing from the
  operating system's entropy. Its output cannot be predicted even by someone
  who has seen everything it produced before.

```python
import secrets
secrets.token_hex(16)     # 32 hex chars, unguessable
secrets.token_urlsafe(16) # for URLs
secrets.choice(items)     # a secure pick
```

## Why predictable randomness is fatal

`random` is reproducible on purpose: seed it with the same value and it replays
the identical sequence. That is a feature for a simulation and a catastrophe for
a token. If a server seeds its generator with something guessable - the current
time is the classic mistake - then an attacker who guesses the seed can replay
every token it will ever issue.

You will write that attack: given the seed, reproduce the exact sequence and
predict the next value. It is not cryptanalysis; it is just running the same
generator. That is how little a predictable source protects.

The defence is simply to use `secrets`, and to give a token enough bytes - 16
(128 bits) is the usual floor - that brute force is hopeless even against a
perfect generator.

## Your turn

In `rng.py`:

- `secure_token(n_bytes=16)` - an unguessable hex token from `secrets`
- `weak_token(seed)` - a 32-bit number from `random` seeded with `seed`; the
  same seed always returns the same number, which is the point
- `predict(seed, n)` - the `n`-th token (1-indexed) a server would issue if it
  seeded `random` with `seed` and handed out `weak_token`-style values in order
- `enough_entropy(n_bytes)` - whether a token of that many random bytes is at
  least 128 bits
