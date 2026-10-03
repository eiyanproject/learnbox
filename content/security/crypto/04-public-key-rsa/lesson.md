---
title: Public-key encryption, by hand
summary: Build textbook RSA from modular arithmetic - key generation, encryption, and the signature that runs it backwards.
order: 4
files: [rsa.py]
run: python rsa.py
hints:
  - "`keygen`: `n = p * q`, `phi = (p - 1) * (q - 1)`. The private exponent is the modular inverse `pow(e, -1, phi)` - but only if `gcd(e, phi) == 1`, so raise `ValueError` when it is not."
  - "`encrypt`/`decrypt` are both `pow(x, exponent, n)` - encryption with the public `e`, decryption with the private `d`."
  - "`sign` is decryption with the private key: `pow(m, d, n)`. `verify` undoes it with the public key and checks you get the message back: `pow(sig, e, n) == m`."
  - "These are the same operation run in opposite directions, which is the whole elegance of RSA."
---

Everything so far shared one secret between both sides. **Public-key**
cryptography breaks that: each party has a **public key** they hand out freely
and a **private key** they never reveal. Anyone can encrypt to you with your
public key; only your private key decrypts. It is what lets two strangers
communicate securely without having met.

RSA is the classic, and its whole engine is modular exponentiation.

## The construction

1. Pick two primes `p` and `q`; let `n = p * q`.
2. Compute `phi = (p - 1) * (q - 1)`.
3. Choose a public exponent `e` with `gcd(e, phi) = 1` (65537 in practice).
4. The private exponent is `d = e^-1 mod phi` - the modular inverse, which
   Python gives you as `pow(e, -1, phi)`.

The public key is `(n, e)`; the private key is `d`. Then:

```text
encrypt:  c = m^e mod n          (anyone, with the public key)
decrypt:  m = c^d mod n          (only you, with the private key)
```

It works because of how `e` and `d` are chosen: raising to `e` then to `d`
(mod n) returns the original. The security rests on **factoring** - recovering
`d` means finding `p` and `q` from `n`, and for large enough primes nobody knows
how to do that in reasonable time.

## Signatures: the same thing backwards

Run it the other way - encrypt with the *private* key - and you get a
**signature**. Only you can produce it, but anyone can check it with your public
key. That proves a message came from you and was not altered:

```text
sign:    s = m^d mod n           (only you)
verify:  m == s^e mod n          (anyone)
```

"Encrypting with the private key" is a fair description of *textbook* RSA only,
and a misleading one in general - signatures and encryption are different
operations with different padding, and other signature schemes (ECDSA, Ed25519)
involve no encryption at all. Real RSA signatures also sign a **hash** of the
message, never the message itself.

> **This is textbook RSA, for learning only.** Real RSA pads the message first
> (OAEP for encryption, PSS for signatures) and uses keys hundreds of digits
> long. Raw RSA on an unpadded message, with the tiny primes here, is insecure -
> you are building it to see the mechanism, not to use it.

## Your turn

In `rsa.py` (all values are integers):

- `keygen(p, q, e=65537)` - return `(n, e, d)`; raise `ValueError` if `e` is not
  coprime with `phi`
- `encrypt(m, e, n)` and `decrypt(c, d, n)`
- `sign(m, d, n)` and `verify(m, sig, e, n)` (returning a bool)
