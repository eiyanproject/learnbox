---
title: Stream ciphers and the nonce trap
summary: A keystream turns XOR into real encryption - until a nonce is reused, at which point the whole thing unravels.
order: 2
files: [stream.py]
run: python stream.py
hints:
  - "`keystream`: build bytes by hashing `key + nonce + counter` for counter 0, 1, 2... concatenating the digests, and cutting to `length`. Use `counter.to_bytes(8, 'big')`."
  - "`stream_xor`: XOR the data with `keystream(key, nonce, len(data))`. The same function encrypts and decrypts."
  - "`recover_xor_of_plaintexts`: just XOR the two ciphertexts together. If they used the same key and nonce, the keystream cancels and you are left with `p1 XOR p2`."
  - "`safe_encrypt`: make a fresh random nonce with `secrets.token_bytes(16)` every time, and return `(nonce, ciphertext)` so it can be decrypted."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **plaintext** | the readable message, before encryption |
| **ciphertext** | the encrypted message |
| **key** | the secret that controls encryption and decryption |
| **XOR** (exclusive or) | combines two bits: 1 when they differ, 0 when they are the same; written `^` |
| **one-time pad** | XOR with a random key as long as the message, used only once; unbreakable, but impractical |
| **stream cipher** | encryption that makes a long keystream from a short key and XORs the message with it |
| **keystream** | the long run of pseudo-random bytes a stream cipher produces |
| **nonce** | a "number used once": a non-secret value that makes each keystream different |
| **counter** | a number that goes 0, 1, 2, ..., used to make each block of keystream different |
| **counter mode** (CTR) | making a keystream from (key, nonce, counter); AES-CTR is the standard example |
| **AES** | the standard modern cipher; Crypto lesson 3 uses it in other ways |
| **concatenate** (`\|\|`) | join byte strings end to end |
| **nonce reuse** | encrypting two messages with the same key and nonce, so both get the same keystream |
| **two-time pad** | the result of nonce reuse: the keystream cancels out and the plaintexts are exposed to each other |
| **AEAD** | encryption that also checks integrity, such as AES-GCM and ChaCha20-Poly1305; nonce reuse breaks these too |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python stream.py` | runs your program: encrypts a message with a fresh nonce and decrypts it again |

### Python names

| Name | What it does |
|---|---|
| `hashlib.sha256(x).digest()` | the SHA-256 of `x` as 32 raw bytes (not hex) |
| `counter.to_bytes(8, "big")` | the counter as 8 bytes, most significant first |
| `out += ...` | appends bytes to `out` |
| `while len(out) < length:` | repeat until there are enough bytes |
| `out[:length]` | only the first `length` bytes |
| `d ^ k` | XOR of two byte values (ints from 0 to 255) |
| `zip(data, stream)` | pairs each data byte with its keystream byte |
| `bytes(... for ...)` | builds a bytes object from a sequence of ints |
| `secrets.token_bytes(16)` | 16 random bytes, for a fresh nonce |
| `return nonce, ciphertext` | returns both values together, as a tuple |
| `.hex()` | bytes shown as hex digits |

---

**XOR** is the basic operation of most encryption. It combines two bits and
gives 1 when they differ, 0 when they are the same. Two facts make it
useful:

- XOR with the same value twice gives back what you started with:
  `p ^ k ^ k == p`. So the same step encrypts and decrypts.
- If `k` is random, `p ^ k` is random too, whatever `p` was.

Take a random key as long as the message, use it once, and XOR is the
**one-time pad**, which is proven unbreakable. The problem is practical: you
would have to share, in secret, a key as long as everything you will ever
send.

## Stream ciphers

A **stream cipher** solves that. From a short key and a **nonce** (a
"number used once"), it generates a long pseudo-random **keystream**, and XORs
the message with it. In this lesson the keystream comes from hashing the key,
the nonce and a **counter**, and joining the results:

```text
keystream  = SHA256(key + nonce + 0) || SHA256(key + nonce + 1) || ...
ciphertext = plaintext XOR keystream
```

(`||` means "followed by".) Each hash gives 32 bytes; keep hashing with the
next counter value until there are enough. This is the same idea as
**AES-CTR** (counter mode), a real, widely used design, with SHA-256 standing
in for AES.

To decrypt, generate the identical keystream from the same key and nonce and
XOR again.

The nonce is **not secret**. It is sent along with the ciphertext. Its only
job is to be **different every time**, so that the same key produces a
different keystream for every message.

## The trap: reusing a nonce

All the security rests on each keystream being used **once**. Encrypt two
messages with the same key **and the same nonce**, and both are XORed with the
identical keystream `K`. Then look at what XORing the two ciphertexts gives:

```text
c1 = p1 XOR K
c2 = p2 XOR K
c1 XOR c2 = p1 XOR p2     # K is XORed in twice, so it cancels out
```

The key has disappeared from the result. What is left is the two plaintexts
mixed together. Anyone who knows or can guess part of one message (a standard
header, a common word) learns the matching part of the other. This is the
**two-time pad**, and it has broken real systems, from wartime ciphers to
Wi-Fi encryption, because reusing a nonce looks harmless.

Modern **AEAD** ciphers such as AES-GCM and ChaCha20-Poly1305 have the same
rule: with a repeated nonce, they leak plaintext and can lose their integrity
protection as well.

The defence has no exceptions: **a fresh, unique nonce for every
encryption.** A random 16-byte nonce from `secrets` makes a repeat
practically impossible. You will write the effect of reuse (recovering
`p1 XOR p2`) and the safe wrapper that makes a new nonce every time.

## Your turn

In `stream.py`:

- `keystream(key, nonce, length)`: `length` pseudo-random bytes, made by
  hashing `key + nonce + counter` for counter 0, 1, 2, ... (each counter as
  8 big-endian bytes), joining the digests and cutting to `length`.
- `stream_xor(key, nonce, data)`: encrypt or decrypt `data` under `key` and
  `nonce`; the same function does both.
- `recover_xor_of_plaintexts(c1, c2)`: given two ciphertexts made with the
  same key and nonce, return `p1 XOR p2`.
- `safe_encrypt(key, data)`: encrypt with a fresh random 16-byte nonce;
  return `(nonce, ciphertext)`.

## Check yourself

1. Why does the same function both encrypt and decrypt?
   *XORing the same keystream twice gives back the original.*
2. Is the nonce secret?
   *No. It is sent with the ciphertext; it only has to be unique.*
3. Two messages were encrypted with the same key and nonce. What does
   `c1 XOR c2` give?
   *`p1 XOR p2`: the keystream cancels out.*
4. How does `safe_encrypt` avoid reuse?
   *It makes a new random nonce for every call.*
5. Why is the one-time pad not used in practice?
   *The key must be as long as all the data and shared in advance.*
