---
title: Agreeing on a key in the open
summary: Diffie-Hellman lets two people derive a shared secret over a line everyone can read - and shows exactly why that is not enough on its own.
order: 5
files: [dh.py]
run: python dh.py
hints:
  - "`public_key`: `pow(g, private, p)` - raise the generator to your private exponent, mod the prime."
  - "`shared_secret`: `pow(their_public, my_private, p)` - raise their public value to your private exponent. Both sides land on the same number."
  - "`derive_key`: turn the shared integer into actual key bytes by hashing it - `hashlib.sha256(str(shared).encode()).hexdigest()`."
  - "The magic is that `(g^a)^b` and `(g^b)^a` are the same mod p, so Alice and Bob compute the same secret without ever sending it."
---

Public-key encryption solved talking to a stranger. **Diffie-Hellman** solves a
subtler problem: two people agreeing on a shared secret key while an
eavesdropper records every byte they exchange - and still not learning the key.

## How it works

Everyone agrees on two public numbers: a large prime `p` and a generator `g`.
Then:

1. Alice picks a secret `a`, sends `A = g^a mod p`.
2. Bob picks a secret `b`, sends `B = g^b mod p`.
3. Alice computes `B^a mod p`; Bob computes `A^b mod p`.

Both get `g^(a*b) mod p` - the **same number** - because the order of the
exponents does not matter. Yet an eavesdropper who saw `g`, `p`, `A` and `B`
cannot get there: recovering `a` from `A = g^a mod p` is the **discrete
logarithm** problem, and for a large prime nobody can do it in time.

The shared integer is then hashed into an actual key.

## The hole this leaves

Diffie-Hellman gives you a shared secret with *someone* - but it never checks
*who*. An attacker sitting in the middle can run the exchange twice: once with
Alice pretending to be Bob, once with Bob pretending to be Alice. Now they share
one key with each side, read and re-encrypt everything in between, and neither
victim can tell. This is the **man-in-the-middle** attack, and it is not a flaw
in the maths - the maths is perfect. It is that key agreement without
**authentication** proves nothing about identity.

That is the missing piece the whole next lesson is about: signatures and
certificates, which bind a key to an identity, so you know the far end is who
they claim. Key exchange and authentication are two halves of one job, and
TLS does both.

## Your turn

In `dh.py`:

- `public_key(g, private, p)` - your public value to send
- `shared_secret(their_public, my_private, p)` - the agreed integer
- `derive_key(shared)` - the shared integer hashed into a hex key
