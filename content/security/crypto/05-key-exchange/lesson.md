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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **key exchange** (key agreement) | two parties arriving at the same secret key over an open network |
| **Diffie-Hellman** (DH) | the first key exchange (1976), built on modular exponentiation |
| **eavesdropper** | someone who can read every message on the line but not change them |
| **prime** (`p`) | the public prime number all the arithmetic is done mod |
| **generator** (`g`) | a public base number; its powers mod `p` cover many different values |
| **private value** (`a`, `b`) | each side's secret random number, never sent |
| **public value** (`A`, `B`) | `g` to the power of the private value, mod `p`; safe to send |
| **shared secret** | the number both sides compute, `g` to the power `a*b`, mod `p` |
| **discrete logarithm** | finding `a` from `g^a mod p`; for a large prime, nobody knows how to do it fast |
| **ECDH** | Diffie-Hellman on elliptic curves: the same idea with much shorter keys |
| **derive a key** | turn the shared number into proper key bytes, here by hashing it |
| **ephemeral** | made fresh for one connection and then thrown away |
| **forward secrecy** | stealing a server's long-term key later does not expose past sessions, because each used an ephemeral DH key |
| **man in the middle** (MITM) | an attacker between the two sides who runs a separate exchange with each |
| **authentication** | proving who the other side is |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python dh.py` | runs your program: Alice and Bob each derive the shared secret, and it checks they match |

### Python names

| Name | What it does |
|---|---|
| `pow(g, a, p)` | `g` to the power `a`, mod `p` |
| `A, B = x, y` | sets two names at once |
| `str(shared)` | the number as text, `"2"` |
| `.encode()` | text turned into bytes, so it can be hashed |
| `hashlib.sha256(...).hexdigest()` | the SHA-256 digest as hex |

---

Public-key encryption lets you send a secret to a stranger. **Diffie-Hellman**
solves a related problem: two people **agreeing** on a shared secret key
while an **eavesdropper** records every byte they send, and still the
eavesdropper does not learn the key.

## The idea, with paint

The Crypto 101 book explains it with paint. Alice and Bob agree in public on
a base colour, say yellow. Each secretly picks a colour of their own and
mixes it into a pot of the yellow. They swap pots in public. Each then adds
their own secret colour again, into the other's pot. Both pots now contain
yellow plus Alice's colour plus Bob's colour: the **same** final colour. An
eavesdropper saw yellow and both mixed pots, but cannot "unmix" paint to get
the secret colours out, so cannot make the final colour.

Diffie-Hellman does the same with numbers. "Mixing" is modular
exponentiation, which is easy to do and very hard to undo.

## How it works

Everyone agrees on two **public** numbers: a large **prime** `p` and a
**generator** `g`. Then:

1. Alice picks a secret `a` and sends `A = g^a mod p`.
2. Bob picks a secret `b` and sends `B = g^b mod p`.
3. Alice computes `B^a mod p`. Bob computes `A^b mod p`.

Both get `g^(a*b) mod p`, the **same number**, because the order of the
exponents does not matter: `(g^b)^a` and `(g^a)^b` are both `g^(a*b)`.

The eavesdropper saw `g`, `p`, `A` and `B`. To get the secret they would need
`a` or `b`, and finding `a` from `A = g^a mod p` is the **discrete
logarithm** problem. For a prime of 2048 bits, nobody knows how to solve it in
any reasonable time.

The textbook example, small enough to follow:

```pycon
>>> p, g = 23, 5                 # public: a toy prime and a generator
>>> a, b = 6, 15                 # private: Alice's and Bob's secrets
>>> A, B = pow(g, a, p), pow(g, b, p)
>>> A, B                         # all that crosses the wire
(8, 19)
>>> pow(B, a, p), pow(A, b, p)   # each side's own calculation
(2, 2)
```

The shared number is not yet a key: it is hashed into proper key bytes
(**derived**), and that key then encrypts the conversation.

```pycon
>>> from dh import derive_key
>>> derive_key(2)
'd4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35'
```

Today most systems use **ECDH**, the same exchange on elliptic curves, which
gives the same strength with much shorter numbers. TLS makes a fresh
(**ephemeral**) DH key for every connection. That gives **forward
secrecy**: even if the server's long-term key is stolen next year, recorded
past sessions stay unreadable, because their keys were thrown away.

## The hole this leaves

Diffie-Hellman gives you a shared secret with **someone**. It never checks
**who**.

An attacker sitting in the middle of the connection, able to change
messages and not just read them, can run the exchange twice: once with
Alice, pretending to be Bob, and once with Bob, pretending to be Alice. Now
the attacker shares one key with each side. They decrypt everything Alice
sends, read it, re-encrypt it for Bob, and neither of them can tell. This is
the **man-in-the-middle** attack.

It is not a flaw in the mathematics, which works perfectly. The problem is
that key agreement without **authentication** proves nothing about who is at
the other end.

The next lesson fills that gap: signatures and certificates, which tie a key
to an identity, so you know the far end is who it claims to be. Key exchange
and authentication are two halves of one job, and TLS (the "s" in https) does
both.

## Your turn

In `dh.py`:

- `public_key(g, private, p)`: the public value to send, `g` to the power
  `private`, mod `p`.
- `shared_secret(their_public, my_private, p)`: the agreed number.
- `derive_key(shared)`: the shared number hashed into a key, the SHA-256 hex
  digest of `str(shared).encode()`.

Run it:

```text
Alice derives 2  Bob derives 2  match: True
```

## Check yourself

1. Which values are sent openly, and which stay secret?
   *`p`, `g`, `A` and `B` are public; `a`, `b` and the shared secret are
   not.*
2. Why do Alice and Bob get the same number?
   *Both compute `g` to the power `a*b`, mod `p`.*
3. What stops an eavesdropper computing the secret?
   *Finding `a` from `g^a mod p`, the discrete logarithm problem.*
4. What does a man in the middle do?
   *Runs a separate exchange with each side and relays between them.*
5. What does Diffie-Hellman need to stop that?
   *Authentication: proof of who the other side is.*
