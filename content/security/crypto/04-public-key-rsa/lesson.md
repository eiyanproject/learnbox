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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **symmetric encryption** | both sides use the same secret key (all the earlier lessons) |
| **public-key encryption** (asymmetric) | each person has a key pair: one key to share, one to keep |
| **public key** | the half you give to everyone; it encrypts to you and checks your signatures |
| **private key** | the half nobody else ever sees; it decrypts and signs |
| **RSA** | the classic public-key system (Rivest, Shamir, Adleman, 1977) |
| **prime** | a whole number greater than 1 divisible only by 1 and itself: 2, 3, 5, 7, 53, 61 |
| **modulus** (`n`) | the product of the two primes, `p * q`; part of the public key |
| **mod** (modulo) | the remainder after division: `17 mod 5` is 2 |
| **modular exponentiation** | `m` to the power `e`, then mod `n`, computed without the huge number in between |
| **phi** (`φ`) | `(p - 1) * (q - 1)`; needed to find the private key, and kept secret |
| **public exponent** (`e`) | the power used to encrypt; 65537 in practice |
| **private exponent** (`d`) | the power used to decrypt; `e * d` leaves remainder 1 when divided by phi |
| **gcd** (greatest common divisor) | the largest number that divides both; `gcd(12, 18)` is 6 |
| **coprime** | having a gcd of 1: no common factor |
| **modular inverse** | the number `d` with `e * d mod phi == 1` |
| **factoring** | splitting `n` back into `p` and `q`; for big primes, nobody knows how to do it fast |
| **signature** | a value only the private key can make and anyone can check with the public key |
| **textbook RSA** | RSA with no padding, as in this lesson; insecure in real use |
| **padding** (OAEP, PSS) | the random structure real RSA adds before encrypting (OAEP) or signing (PSS) |
| **ECDSA, Ed25519** | other signature systems, based on elliptic curves rather than RSA |
| **hybrid encryption** | public-key encryption of a random symmetric key, which then encrypts the data |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python rsa.py` | runs your program: makes the toy key pair and encrypts and decrypts 65 |

### Python names

| Name | What it does |
|---|---|
| `from math import gcd` | loads the greatest common divisor function |
| `pow(m, e, n)` | `m` to the power `e`, mod `n`, computed quickly |
| `pow(e, -1, phi)` | the modular inverse of `e` mod `phi` |
| `x % n` | the remainder of `x` divided by `n` |
| `raise ValueError("...")` | stops the function with an error that says what was wrong |
| `return n, e, d` | returns three values together, as a tuple |
| `p, q, e = 61, 53, 17` | sets three names at once |

---

Everything so far used one secret shared by both sides (**symmetric**
encryption). That leaves a hard question: how do two people who have never
met agree on a secret in the first place, over a network anyone can listen
to?

**Public-key** cryptography answers it. Each person has two keys that belong
together:

- a **public key**, which they hand out freely;
- a **private key**, which they never show to anyone.

Anyone can encrypt a message to you with your public key, and only your
private key can decrypt it. **RSA** is the classic system, and its engine is
one operation: raising a number to a power and taking the remainder.

## A little modular arithmetic

`a mod n` is the remainder when `a` is divided by `n`: `17 mod 5` is 2,
because 17 is 3 fives and 2 left over. Python writes it `17 % 5`.
**Modular exponentiation**, `m` to the power `e` mod `n`, is
`pow(m, e, n)`, and Python computes it quickly even for numbers hundreds of
digits long.

Two more ideas:

- The **gcd** (greatest common divisor) of two numbers is the biggest number
  that divides both. Two numbers whose gcd is 1 are **coprime**.
- The **modular inverse** of `e` mod `phi` is the number `d` for which
  `e * d mod phi` is 1. It exists only when `e` and `phi` are coprime.
  Python finds it with `pow(e, -1, phi)`.

## Building a key pair

1. Pick two **primes** `p` and `q`, and multiply them: `n = p * q`.
2. Compute `phi = (p - 1) * (q - 1)`.
3. Choose a public exponent `e` that is coprime with `phi`. In practice it is
   always 65537.
4. The private exponent `d` is the modular inverse of `e` mod `phi`.

The public key is `(n, e)`. The private key is `d`. Then:

```text
encrypt:  c = m^e mod n          (anyone, with the public key)
decrypt:  m = c^d mod n          (only you, with the private key)
```

Here is the classic worked example, with primes small enough to check by
hand. The message is the number 65.

```pycon
>>> p, q, e = 61, 53, 17         # toy primes; real ones are hundreds of digits long
>>> n, phi = p * q, (p - 1) * (q - 1)
>>> n, phi
(3233, 3120)
>>> d = pow(e, -1, phi)
>>> d
2753
>>> e * d % phi                  # the definition of the inverse
1
>>> c = pow(65, e, n)            # encrypt the message 65
>>> c
2790
>>> pow(c, d, n)                 # decrypt
65
```

It works because of how `d` was chosen: raising to `e` and then to `d`
(mod `n`) always gives the original number back.

### Why it is secure

Everything public, `n` and `e`, is not enough to find `d`: for that you need
`phi`, and for `phi` you need `p` and `q`. Getting `p` and `q` from `n` is
called **factoring**. For `3233` it is easy; for an `n` of 617 digits (a
2048-bit key), nobody knows a way to do it in any reasonable time. That is the
whole basis of RSA's security.

If `e` and `phi` are not coprime, `e` has no inverse and there is no private
key. Your `keygen` must refuse with a `ValueError`.

## Signatures: the same operation the other way round

Run it the other way, raising to the **private** exponent, and you get a
**signature**. Only the private key's owner can make it, and anyone can check
it with the public key. That proves who sent a message and that it was not
changed.

```text
sign:    s = m^d mod n           (only you)
verify:  s^e mod n == m          (anyone)
```

```pycon
>>> s = pow(65, d, n)            # sign 65
>>> s
588
>>> pow(s, e, n) == 65           # verify with the public key
True
```

"Signing is encrypting with the private key" is true only of this
**textbook** form. Real RSA signatures and RSA encryption use different
padding, and other signature systems (ECDSA, Ed25519) do no encryption at
all. Real signatures also sign a **hash** of the message, never the whole
message.

### This is textbook RSA, for learning only

Real RSA adds random **padding** before the maths: **OAEP** for encryption
and **PSS** for signatures. Without it, the same message always encrypts to
the same ciphertext, so an attacker can test guesses, and ciphertexts can be
combined in ways the owner did not intend. Real keys are also 2048 bits or
more. Public-key operations are slow, so real systems use **hybrid
encryption**: RSA (or key exchange, next lesson) protects a random symmetric
key, and that key encrypts the data. You are building RSA to see how it
works, not to use it.

## Your turn

In `rsa.py` (all values are integers):

- `keygen(p, q, e=65537)`: return `(n, e, d)`. Raise `ValueError` if `e` is
  not coprime with `phi` (`math.gcd(e, phi) != 1`).
- `encrypt(m, e, n)` and `decrypt(c, d, n)`.
- `sign(m, d, n)` and `verify(m, sig, e, n)`; `verify` returns `True` or
  `False`.

Run it:

```text
public key: (3233, 17)  private d: 2753
65 encrypts to 2790 and back to 65
```

## Check yourself

1. Which key encrypts a message to you, and which decrypts it?
   *Your public key encrypts; your private key decrypts.*
2. What is `pow(e, -1, phi)`?
   *The modular inverse of `e`: the private exponent `d`.*
3. What would an attacker need to find `d` from the public key?
   *The primes `p` and `q`, by factoring `n`.*
4. Why must `keygen` reject an `e` that is not coprime with `phi`?
   *Then `e` has no inverse, so no private key exists.*
5. Why is textbook RSA unsafe in practice?
   *No padding: it is deterministic and malleable, and the keys here are
   tiny.*
