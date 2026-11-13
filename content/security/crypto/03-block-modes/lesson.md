---
title: Block cipher modes
summary: Why encrypting each block independently leaks the shape of your data, and how chaining with an IV hides it.
order: 3
files: [modes.py]
run: python modes.py
hints:
  - "`block_transform` is given to you - a stand-in for a real cipher. Use it as the per-block step; the lesson is about the mode around it, not the cipher."
  - "`ecb_encrypt`: split data into `bs`-byte blocks and transform each one on its own. Identical input blocks give identical output blocks - that is the leak."
  - "`has_repeated_blocks`: cut the ciphertext into `bs`-byte blocks and check whether any two are equal."
  - "`cbc_encrypt`: XOR each plaintext block with the previous ciphertext block (the first uses the IV) before transforming. Now identical plaintext blocks encrypt differently."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **block cipher** | a cipher that encrypts a fixed-size piece of data at a time |
| **block** | that fixed-size piece; 16 bytes for AES |
| **AES** | the standard block cipher; 16-byte blocks, keys of 16, 24 or 32 bytes |
| **mode of operation** (mode) | the rule for encrypting a message longer than one block |
| **ECB** (electronic codebook) | the mode that encrypts every block on its own; never use it |
| **CBC** (cipher block chaining) | the mode that mixes each block with the previous ciphertext block first |
| **CTR, GCM** | counter mode (previous lesson) and its authenticated form, the usual modern choice |
| **pattern leak** | when the shape of the data (repeats, structure) shows through the encryption |
| **initialisation vector** (IV) | a random, non-secret block that starts the chain in CBC |
| **unpredictable** | cannot be guessed in advance; CBC needs this from its IV, not just uniqueness |
| **chosen plaintext** | when an attacker can get messages of their choice encrypted |
| **BEAST** | a 2011 attack on TLS 1.0, which used predictable CBC IVs |
| **padding** | extra bytes that make a message a whole number of blocks (this lesson's data already is one) |
| **deterministic** | the same input always gives the same output |
| **stand-in** | a simple replacement used so the lesson can focus on something else |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python modes.py` | runs your program: checks ECB and CBC output for repeated blocks |

### Python names

| Name | What it does |
|---|---|
| `block_transform(key, block)` | given to you: a keyed scramble standing in for AES, **not** secure |
| `chunks(data, bs)` | given to you: `data` cut into a list of `bs`-byte blocks |
| `range(0, len(data), bs)` | 0, `bs`, `2*bs`, ...: where each block starts |
| `b"".join(blocks)` | the blocks glued back into one bytes object |
| `set(blocks)` | the distinct blocks, with repeats removed |
| `len(set(x)) != len(x)` | `True` when `x` contains a repeat |
| `prev = iv` | the "previous ciphertext block", which for the first block is the IV |
| `b ^ p` | XOR of two bytes |
| `out.append(c)` | adds a ciphertext block to the list |
| `b"YELLOW SUBMARINE" * 3` | the 16-byte block repeated three times |
| `bytes(16)` | 16 zero bytes |
| `bytes(range(16))` | the bytes 0, 1, 2, ..., 15 |

---

Real **block ciphers** like AES encrypt a fixed-size **block** at a time,
16 bytes for AES. A longer message has to be cut into blocks, and the
**mode of operation** is the rule for how each block is encrypted and how
they fit together. A strong cipher in a bad mode is still broken, and this is
where real systems often go wrong.

## ECB: the mode never to use

The obvious approach is to encrypt each block on its own. It is called
**ECB**, and it has one fatal property: **identical plaintext blocks give
identical ciphertext blocks**.

```pycon
>>> from modes import ecb_encrypt, chunks
>>> key = bytes(range(16))
>>> c = ecb_encrypt(key, b"YELLOW SUBMARINE" * 3)    # three identical blocks
>>> [block.hex() for block in chunks(c, 16)]
['9d29115fa2aeaf3935d8c9fb53693d19', '9d29115fa2aeaf3935d8c9fb53693d19', '9d29115fa2aeaf3935d8c9fb53693d19']
```

Nobody can read the plaintext, but anyone can see that it repeats. The cipher
is fine, yet the **pattern** of the data shows straight through. The famous
example is an image encrypted with ECB: the outline is still visible, because
every area of one colour becomes the same repeated ciphertext block.
Repeated records, fixed headers and padded fields all leak the same way.

That makes ECB easy to spot. If a ciphertext contains repeated blocks, it
was almost certainly ECB over repetitive data. That check is the detector
you will write.

## CBC: chaining hides the pattern

The fix is to make each block depend on the one before. **CBC** XORs each
plaintext block with the **previous ciphertext block** before encrypting
it. Two identical plaintext blocks are now mixed with different values, so
they come out different.

The first block has no previous block, so it is XORed with an
**initialisation vector** (IV): a random block, sent openly with the
ciphertext.

```text
ECB:  c[i] = E(p[i])                 same p[i]  ->  same c[i]    (leaks)
CBC:  c[i] = E(p[i] XOR c[i-1])      same p[i]  ->  different    (hidden)
      c[0] = E(p[0] XOR IV)
```

Here `E` is the block cipher and `c[i-1]` the previous ciphertext block.

```pycon
>>> from modes import cbc_encrypt
>>> c = cbc_encrypt(key, bytes(16), b"YELLOW SUBMARINE" * 3)
>>> [block.hex()[:8] for block in chunks(c, 16)]      # first 8 hex digits of each
['9d29115f', 'c6e5609f', 'ddfe0272']
```

### The IV must be unpredictable

For CBC, a unique IV is **not** enough: it must be **unpredictable**. If an
attacker can predict the next IV and can get some text of their own
encrypted (a **chosen plaintext**), they can build a block that tests a guess
about an earlier secret block; a matching ciphertext confirms the guess. The
**BEAST** attack did exactly this to TLS 1.0, which used the last ciphertext
block of one message as the IV of the next.

So make every CBC IV with `secrets.token_bytes(16)`. (Counter-mode nonces,
from the last lesson, only need to be unique: a different rule for a
different mode.) Today, the usual choice is an authenticated mode such as
**AES-GCM**, which also detects tampering.

### About `block_transform`

So that this lesson is about the mode, not the cipher, you are given
`block_transform`, a simple keyed scramble standing in for AES. It is **not**
secure on its own. The point is the structure around it: ECB leaks patterns
and CBC hides them, however strong the cipher in the middle.

## Your turn

In `modes.py` (the data is always a whole number of `bs`-byte blocks):

- `ecb_encrypt(key, data, bs=16)`: apply `block_transform(key, block)` to
  each block on its own, and join the results.
- `has_repeated_blocks(data, bs=16)`: `True` when any two `bs`-byte blocks
  are identical. This is your ECB detector.
- `cbc_encrypt(key, iv, data, bs=16)`: XOR each plaintext block with the
  previous **ciphertext** block (the first with `iv`), then apply
  `block_transform`.

Run it:

```text
ECB repeats? True
CBC repeats? False
```

## Check yourself

1. Why does ECB leak information even with a perfect cipher?
   *Identical plaintext blocks give identical ciphertext blocks.*
2. How do you tell that a ciphertext was probably made with ECB?
   *It contains repeated blocks.*
3. In CBC, what is each plaintext block XORed with?
   *The previous ciphertext block; the first one with the IV.*
4. Is the IV secret?
   *No, but for CBC it must be unpredictable.*
5. What did TLS 1.0 get wrong, which BEAST used?
   *Its next IV was predictable: the last ciphertext block.*
